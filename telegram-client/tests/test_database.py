import asyncio
import os

from sqlalchemy import select

from karlancer_automation.database import (
    create_database_engine,
    create_session_factory,
    create_tables,
)
from karlancer_automation.models import Project
from karlancer_automation.telegram.client import save_project


async def main():
    engine = create_database_engine()
    session_factory = create_session_factory(engine)
    message_id = 999999999

    try:
        await create_tables(engine)

        # پاک‌سازی رکورد آزمایشی قبلی
        async with session_factory() as session:
            result = await session.execute(
                select(Project).where(
                    Project.source == "karlancer",
                    Project.source_message_id == str(message_id),
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                await session.delete(existing)
                await session.commit()

        sample_message = """
عنوان پروژه: طراحی سایت فروشگاهی
بودجه: ۱۰ میلیون تومان
مهلت: ۱۰ روز
توضیحات: طراحی یک فروشگاه اینترنتی واکنش‌گرا
"""

        first = await save_project(
            session_factory,
            message_id,
            sample_message,
        )

        second = await save_project(
            session_factory,
            message_id,
            sample_message,
        )

        print("First save:", first)
        print("Second save:", second)
        print("Duplicate prevention:", first and not second)

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
