from includes.utils._sub import configure_page
from includes.core.globals.entry import app_context

from includes.core.metadata import MetaData
from includes.services.exam.answer_sheet import AnsSeet
from includes.services.exam.results import Results


async def process_exam(roots=None):
    """Active exam database"""
    await app_context.db.configure_exam()
    member = await app_context.setting.member()

    if not member:
        configure_page(template="query/login_required", title="Login Required", suffix=True)
        return {"page_type": "required"}

    if app_context.route.scope_slug == "result":
        template = await Results.index()
        configure_page(template=template, title="VV:Result", suffix=True)
        return {"page_type": "page"}

    if app_context.route.scope_slug == "answer_sheet":
        template, data = await AnsSeet.index()
        configure_page(template=template, title=app_context.response.get("title", "VV:AnsSeet"), suffix=True)
        data["page_type"] = "page"
        return data

    configure_page(template="query/exam", title="Exam", suffix=True)
    return {"page_type": "page"}
