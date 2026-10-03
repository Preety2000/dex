import json
import base64

from sqlalchemy import asc, desc, or_, select
from includes.core.config import app_context, main_database
from datetime import datetime
from sqlalchemy.orm import selectinload

from includes.core.paginator import NewQueryPaginator
from includes.db.connection import active_primary_db
from includes.db.dataclass import MemberRole
from includes.db.models.owner import Members, VerifyIdentity
from includes.core.security import _Security
from includes.schemas.cache.member import MemberCache
from includes.schemas.router_schema import DynamicURLRoute
from includes.utils.exm import get_folder_key
from includes.utils.meb import get_email_folder_info
from includes.utils.utils import get_query_value, redirect_back
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
    async def teacher_indentity():
        verify = {}
        error = {}
        verify["status"] = 0
        verify["error"] = error

        app_context.response["formView"] = True
        app_context.response["verify"] = verify
        data_querys = []

        # for i in app_context.db.query(VerifyIdentity).all():
        #     app_context.db.delete(i)

        # app_context.db.commit()

        for item in (
            app_context.db.query(VerifyIdentity).order_by(desc(VerifyIdentity.id)).all()
        ):
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

        app_context.response["rejection_reasons"] = rejection_reasons
        app_context.response["data_querys"] = data_querys

        return

    @classmethod
    async def _get_member(cls):
        item = get_query_value("item")

        if not item:
            app_context.response["error"] = "Member ID is required."
            return None

        msb = await app_context.db.configure_main()

        member = msb.query(Members).filter(Members.id == item).first()

        if member is None:
            app_context.response["error"] = "Member not found."
            return None

        return member

    @classmethod
    async def block(cls):
        force = int(get_query_value("force", 0))
        member = await cls._get_member()

        if member is None:
            return False

        if member.status == MemberRole.BLOCKED:
            app_context.response["error"] = "Member is already blocked."
            return False

        if member.status == MemberRole.TEACHER and force != 1:
            app_context.response["error"] = app_context.response["error"] = (
                "Teacher members cannot be blocked. "
                "If you still want to block this member, <a href='/members/block?item={member.id}&action=block&force=1'>click here</a> to continue."
            )

            return False

        member.status = MemberRole.BLOCKED
        app_context.db.commit()

        return True

    @classmethod
    async def unblock(cls):
        member = await cls._get_member()

        if member is None:
            return False

        if member.status != MemberRole.BLOCKED:
            app_context.response["error"] = "Member is not blocked."
            return False

        member.status = MemberRole.PENDING
        app_context.db.commit()

        return True

    @classmethod
    async def get_member_list(cls):

        def transform(record):
            data = MemberCache._cache(record)
            data["img"] = (
                f"/media/u/{get_email_folder_info(data["id"])}/{data.get('image_src', _Security.short_encode('image.png'))}"
            )
            return data

        db = active_primary_db()
        data = await NewQueryPaginator.paginate(
            db=db,
            limit=10,
            types="query",
            model=Members,
            transform=transform,
            query=(select(Members).options(
                selectinload(Members.identity),
                selectinload(Members.last_login),
            )),
        )
        return data.records

    @classmethod
    async def index(cls, roots: DynamicURLRoute):
        if roots.scope_slug == "block":
            await cls.block()
            redirect_back("admin/member")

        if roots.scope_slug == "unblock":
            await cls.unblock()
            redirect_back("admin/member")

        data = await cls.get_member_list()

        app_context.response["data_querys"] = data
        return "admin/member"
