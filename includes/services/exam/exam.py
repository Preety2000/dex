from includes.src.request import Request
from includes.database.connection import db
from includes.utils._sub import configure_page
from includes.services.exam.results import Results
from includes.services.exam.answer_sheet import AnsSeet


async def process_exam(request: Request = None):
    """Active exam database"""
    await db.configure_exam()
    member = await request.state.setting.member()

    if not member:
        configure_page(
            request.state.metadata,
            template="query/login_required",
            title="Login Required",
            suffix=True,
        )
        return {"page_type": "required"}

    if request.state.roote.scope == "result":
        template = await Results.index(request)
        configure_page(
            request.state.metadata,
            template=template,
            title="VV:Result",
            suffix=True,
        )
        return {"page_type": "page"}

    if request.state.roote.scope == "answer_sheet":
        template, data = await AnsSeet.index(request)
        configure_page(
            request.state.metadata,
            template=template,
            title=request.state.response.get("title", "VV:AnsSeet"),
            suffix=True,
        )
        data["page_type"] = "page"
        return data

    configure_page(
        request.state.metadata, template="query/exam", title="Exam", suffix=True
    )
    return {"page_type": "page"}
