from includes.core.config import MASTER_KEY
from includes.core.globals.entry import app_context
from includes.core.globals.fun import random_string
from includes.core.security import _Security
from includes.db.connection import active_primary_db
from includes.db.models.owner import Members, MemberSession
from includes.db.models.utils import TimeStamp
from includes.schemas.cache.member import MemberCache
from includes.utils.utils import get_post_value


class LogoutHandler:

    @classmethod
    async def logout_all_sessions(cls, db, member_id: int):
        """User ke saare active sessions ko ek saath logout karta hai (Bulk Update)."""
        db.query(MemberSession).filter(
            MemberSession.user_id == member_id, MemberSession.is_active == True
        ).update(
            {
                MemberSession.is_active: False,
                MemberSession.logout_time: TimeStamp.now_iso(),
            },
            synchronize_session=False,
        )
        db.commit()

    @classmethod
    async def process_logout(cls):
        """Current session ya all sessions ko safely terminate karta hai."""
        db_session = await active_primary_db()
        session_type = await get_post_value("session")
        system_user = await app_context.setting.member()

        if not system_user:
            return {
                "session_error": True,
                "message": "Invalid or expired session. Please login again.",
            }

        member = (
            db_session.query(Members).filter_by(email=system_user["email"]).first()
        )

        if not member:
            return {"session_error": True, "message": "User account not found."}

        device_key = None

        # 1. Current Session ID extracting & deactivating
        try:
            master_key = app_context.setting.setting_session.get("MASTER_KEY", "")
            if "///" in master_key:
                device_key = master_key.split("///")[1]
                session_db_id = int(_Security.short_decode(device_key))

                user_session = (
                    db_session.query(MemberSession)
                    .filter_by(id=session_db_id, user_id=member.id)
                    .first()
                )

                if user_session:
                    user_session.is_active = False
                    user_session.logout_time = TimeStamp.now_iso()
                    db_session.commit()

        except Exception:
            device_key = None

        # Devices list updating
        devices = list(member.device or [])
        if session_type:
            member.device = []
            await cls.logout_all_sessions(db_session, member.id)
        else:
            if device_key and device_key in devices:
                devices.remove(device_key)
            member.device = devices

        # Cookie & Master key update
        app_context.setting.setting_session["MASTER_KEY"] = MASTER_KEY
        app_context.setting.update_cookie()

        # Cache
        MemberCache._cache(member)
        db_session.commit()

        return {
            "logout": True,
            "params": [
                True,
                [None, False],
                [
                    54,
                    {"MASTER_KEY": None},
                    random_string(40),
                ],
            ],
        }
