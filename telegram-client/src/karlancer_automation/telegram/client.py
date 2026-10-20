import asyncio
import logging

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from telethon import TelegramClient, events
from telethon.errors import (
    ApiIdInvalidError,
    AuthKeyUnregisteredError,
    FloodWaitError,
)

from karlancer_automation.config import get_settings
from karlancer_automation.database import (
    create_database_engine,
    create_session_factory,
    create_tables,
)
from karlancer_automation.models import Project
from karlancer_automation.parser import parse_project_message

logger = logging.getLogger(__name__)
KARLANCER_BOT = "KarlancerBot"


def create_telegram_client() -> TelegramClient:
    settings = get_settings()

    if settings.telegram_api_id is None or settings.telegram_api_hash is None:
        raise RuntimeError(
            "Telegram API credentials are missing. "
            "Set TELEGRAM_API_ID and TELEGRAM_API_HASH in .env."
        )

    return TelegramClient(
        settings.telegram_session,
        settings.telegram_api_id,
        settings.telegram_api_hash.get_secret_value(),
    )


async def save_project(
    session_factory: async_sessionmaker[AsyncSession],
    message_id: int,
    message_text: str,
) -> bool:
    parsed = parse_project_message(message_text)

    async with session_factory() as session:
        statement = (
            insert(Project)
            .values(
                source="karlancer",
                source_message_id=str(message_id),
                title=parsed.title,
                description=parsed.description,
                budget=parsed.budget,
                deadline=parsed.deadline,
                status="new",
            )
            .on_conflict_do_nothing(constraint="uq_project_source_message")
            .returning(Project.id)
        )

        result = await session.execute(statement)
        project_id = result.scalar_one_or_none()

        await session.commit()

        if project_id is None:
            logger.info("Duplicate message skipped: %s", message_id)
            return False

        logger.info("Project saved. ID: %s", project_id)
        return True


async def run_client() -> None:
    engine = create_database_engine()
    client = create_telegram_client()

    try:
        await create_tables(engine)
        session_factory = create_session_factory(engine)

        @client.on(events.NewMessage(chats=KARLANCER_BOT))
        async def handle_new_message(
            event: events.NewMessage.Event,
        ) -> None:
            message_text = event.raw_text.strip()

            if not message_text:
                return

            logger.info(
                "New message received from @%s (message ID: %s)",
                KARLANCER_BOT,
                event.message.id,
            )

            print("\n" + "=" * 60)
            print(message_text)
            print("=" * 60)

            try:
                await save_project(
                    session_factory=session_factory,
                    message_id=event.message.id,
                    message_text=message_text,
                )
            except Exception:
                logger.exception(
                    "Failed to save message ID %s",
                    event.message.id,
                )

        await client.start()

        me = await client.get_me()
        logger.info(
            "Telegram connected. Account ID: %s",
            me.id if me else "unknown",
        )
        logger.info("Listening for messages from @%s", KARLANCER_BOT)

        await client.run_until_disconnected()

    except ApiIdInvalidError:
        logger.error("Telegram API ID or API hash is invalid.")
        raise
    except AuthKeyUnregisteredError:
        logger.error("Telegram session is invalid or revoked.")
        raise
    except FloodWaitError as exc:
        logger.error("Telegram rate limit: wait %s seconds.", exc.seconds)
        raise
    finally:
        await client.disconnect()
        await engine.dispose()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        logger.info("Telegram client stopped.")


if __name__ == "__main__":
    main()
