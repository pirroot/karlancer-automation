from karlancer_automation.parser import parse_project_message


def test_parse_project_message():
    message = """
عنوان پروژه: طراحی سایت فروشگاهی
بودجه: ۱۵ تا ۲۰ میلیون تومان
مهلت: ۱۰ روز

توضیحات:
به یک برنامه‌نویس برای طراحی فروشگاه اینترنتی نیاز داریم.
"""

    project = parse_project_message(message)

    assert project.title == "طراحی سایت فروشگاهی"
    assert project.budget == "۱۵ تا ۲۰ میلیون تومان"
    assert project.deadline == "۱۰ روز"
    assert "فروشگاه اینترنتی" in project.description
    assert project.source_text == message


def test_parse_message_without_optional_fields():
    message = "سلام، برای پروژه خود به برنامه‌نویس نیاز داریم."

    project = parse_project_message(message)

    assert project.title is None
    assert project.budget is None
    assert project.deadline is None
    assert project.description == message
