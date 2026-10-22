import json
import base64

from includes.src.request import Request
from sqlalchemy import asc, desc, or_, select
from includes.core.globals.entry import app_context

from datetime import datetime
from sqlalchemy.orm import selectinload

from includes.core.globals.route_context import Route
from includes.core.paginator import NewQueryPaginator
from includes.database.connection import config_primary_db, db
from includes.database.dataclass.dataclass import MemberRole
from includes.database.models.primary import Members, VerifyIdentity
from includes.core.security import _Security
from includes.schemas.cache.member import MemberCache
from includes.utils.exm import get_folder_key
from includes.utils.meb import get_email_folder_info
from includes.utils.utils import redirect_back
from includes.utils.exm import rejection_reasons

divider = "_"


def object_to_random_string(obj):
    json_str = json.dumps(obj)
    encoded = base64.urlsafe_b64encode(json_str.encode()).decode()
    return encoded


def random_string_to_object(encoded_str, value=None):
    try:
        decoded = base64.urlsafe_b64decode(encoded_str.encode()).decode()
        return json.loads(decoded)
    except Exception as e:
        print("Error:", e)
        return value


def timestamp_to_int(timestamp):
    """Convert timestamp (str/int/float/datetime) to int."""
    try:
        if isinstance(timestamp, datetime):
            return int(timestamp.timestamp())
        return int(float(timestamp))
    except (TypeError, ValueError):
        return 0


class IsMember:

    @staticmethod
    async def teacher_indentity(request: Request = None):
        verify = {}
        error = {}
        verify["status"] = 0
        verify["error"] = error

        request.state.response["formView"] = True
        request.state.response["verify"] = verify
        data_querys = []

        # for i in db.query(VerifyIdentity).all():
        #     db.delete(i)

        # db.commit()

        for item in db.query(VerifyIdentity).order_by(desc(VerifyIdentity.id)).all():
            uid = get_folder_key(int(item.user_id))
            member = await MemberCache.get_with_id(
                item.user_id,
                [
                    "name",
                    "img",
                    "phone",
                    "email",
                    "biography",
                    "timestamp",
                    "last_login",
                ],
            )
            data_querys.append(
                {
                    "id": item.id,
                    "info": item.info,
                    "status": item.status,
                    "subject": item.subject,
                    "rejects": item.reject_message,
                    "experience": item.experience,
                    "document_name": item.document_name,
                    "document_url": f"/media/exnr/{uid}/{item.document}",
                    "request_timestamp": timestamp_to_int(item.timestamp),
                    **(member or {}),
                }
            )

        request.state.response["rejection_reasons"] = rejection_reasons
        request.state.response["data_querys"] = data_querys

        return

    @classmethod
    async def _get_member(cls, request):
        item = request.query_params.get("item")

        if not item:
            request.state.response["error"] = "Member ID is required."
            return None

        msb = await db.configure_main()

        member = msb.query(Members).filter(Members.id == item).first()

        if member is None:
            request.state.response["error"] = "Member not found."
            return None

        return member

    @classmethod
    async def block(cls, request):
        force = int(request.query_params.get("force", 0))
        member = await cls._get_member(request)

        if member is None:
            return False

        if member.status == MemberRole.BLOCKED:
            request.state.response["error"] = "Member is already blocked."
            return False

        if member.status == MemberRole.TEACHER and force != 1:
            request.state.response["error"] = request.state.response["error"] = (
                "Teacher members cannot be blocked. "
                "If you still want to block this member, <a href='/members/block?item={member.id}&action=block&force=1'>click here</a> to continue."
            )

            return False

        member.status = MemberRole.BLOCKED
        db.commit()

        return True

    @classmethod
    async def unblock(cls, request):
        member = await cls._get_member(request)

        if member is None:
            return False

        if member.status != MemberRole.BLOCKED:
            request.state.response["error"] = "Member is not blocked."
            return False

        member.status = MemberRole.PENDING
        db.commit()

        return True

    @classmethod
    async def get_member_list(cls, request: Request = None):

        async def transform(record):
            data = await MemberCache._cache(record)
            data["img"] = (
                f"/media/u/{get_email_folder_info(data["id"])}/{data.get('image_src', _Security.short_encode('image.png'))}"
            )
            return data

        db = config_primary_db()
        data = await NewQueryPaginator.paginate(
            db=db,
            limit=10,
            types="query",
            model=Members,
            request=request,
            transform=transform,
            query=(select(Members).options(selectinload(Members.identity))),
        )
        return data.records

    @classmethod
    async def index(cls, roots: Route, request):
        if roots.scope == "block":
            await cls.block(request)
            redirect_back(request, "admin/member")

        if roots.scope == "unblock":
            await cls.unblock(request)
            redirect_back(request, "admin/member")

        data = await cls.get_member_list(request)

        request.state.response["data_querys"] = data
        return "admin/member"
