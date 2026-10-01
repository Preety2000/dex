from sqlalchemy import and_
from includes.core.globals.entry import app_context
from includes.db.dataclass import MemberRole, TeacherStatus
from includes.db.models.owner import Members, VerifyIdentity
from includes.schemas.cache.member import MemberCache
from includes.db.models.utils import TimeStamp

from sqlalchemy.orm.attributes import flag_modified

from includes.utils.utils import get_post_value, json_response


class ActionForm:

    @staticmethod
    async def verify_teacher_identity():
        email = await get_post_value("email")
        verification_id = await get_post_value("id")
        approve = await get_post_value("verify", False)
        block_private = await get_post_value("block_private")
        block_teacher = await get_post_value("block_teacher")
        rejection_message = await get_post_value("rejection_message")
        reasons = await get_post_value("reasons")

        if not verification_id or not email:
            return {"status": False, "message": "Missing required fields"}

        identity = (
            app_context.db.query(VerifyIdentity)
            .filter(VerifyIdentity.id == verification_id)
            .first()
        )

        if not identity:
            return {"status": False, "message": "Verification record not found"}

        member = (
            app_context.db.query(Members)
            .filter(
                Members.id == identity.user_id,
                Members.email == email,
            )
            .first()
        )

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

        app_context.db.commit()
        app_context.db.refresh(member)
        app_context.db.refresh(identity)

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
    async def index(detail):
        if (
            app_context.request.referer
            and app_context.request.referer.path == "/admin/teacher-verify-indentity"
        ):
            query = await ActionForm.verify_teacher_identity()
            return json_response(query)

        return {}
