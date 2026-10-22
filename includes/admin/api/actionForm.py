from includes.src.request import Request
from sqlalchemy import and_, select
from includes.core.globals.entry import app_context
from includes.database.connection import config_primary_db
from includes.database.dataclass.dataclass import MemberRole, TeacherStatus
from includes.database.models.primary import Members, VerifyIdentity
from includes.schemas.cache.member import MemberCache
from includes.database.models.utils import TimeStamp

from sqlalchemy.orm.attributes import flag_modified

from includes.utils.utils import get_post_value, json_response


class ActionForm:

    @staticmethod
    async def verify_teacher_identity(request):
        email = await get_post_value(request, "email")
        verification_id = await get_post_value(request, "id")
        approve = await get_post_value(request, "verify", False)
        block_private = await get_post_value(request, "block_private")
        block_teacher = await get_post_value(request, "block_teacher")
        rejection_message = await get_post_value(request, "rejection_message")
        reasons = await get_post_value(request, "reasons")

        if not verification_id or not email:
            return {"status": False, "message": "Missing required fields"}

        db = await config_primary_db()
        identity = db.execute(
            select(VerifyIdentity).where(VerifyIdentity.id == verification_id)
        ).scalar_one_or_none()

        if not identity:
            return {
                "status": False,
                "message": "Verification record not found",
            }

        member = db.execute(
            select(Members).where(
                Members.id == identity.user_id,
                Members.email == email,
            )
        ).scalar_one_or_none()

        if not member:
            return {"status": False, "message": "Teacher not found"}

        if approve:
            member.status = MemberRole.TEACHER
            identity.status = TeacherStatus.VERIFIED
            identity.verify_timestamp = TimeStamp.now_iso()

            label = "Unverify"
            css = "success-list"

        else:
            if not reasons:
                return {
                    "status": False,
                    "message": "Please select a reason for rejecting the verification request.",
                }

            identity.reasons = reasons
            identity.status = (
                TeacherStatus.BLOCKED
                if block_teacher == "Yes"
                else TeacherStatus.UNVERIFIED
            )

            member.status = (
                MemberRole.BLOCKED if block_private == "Yes" else MemberRole.STUDENT
            )

            if rejection_message:
                identity.reject_message.append(
                    {
                        "message": rejection_message,
                        "timestamp": TimeStamp.now_timestamp(),
                    }
                )
                flag_modified(identity, "reject_message")

            label = "Verify"
            css = None

        db.commit()
        db.refresh(member)
        db.refresh(identity)

        await MemberCache.delete_cache(member.id)

        return {
            "status": True,
            "__ac": 1001,
            "id": identity.id,
            "ids": f"ls_{identity.id}",
            "cls": css,
            "inner": label,
            "jsname": "teacherVerifyUnVerify",
        }

    @staticmethod
    async def index(detail, request: Request = None):
        if (
            request.state.referer
            and request.state.referer.path == "/admin/teacher-verify-indentity"
        ):
            query = await ActionForm.verify_teacher_identity(request)
            return json_response(query)

        return {}
