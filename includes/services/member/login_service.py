from sqlalchemy import inspect

from includes.db.models.utils import TimeStamp
from includes.core.globals.entry import app_context
from includes.core.security import _Security
from includes.db.models.owner import Members, MemberSession
from includes.schemas.cache.member import MemberCache
from includes.utils.utils import get_query_value


def complete_login(member: Members, db) -> str | None:
    device_id = app_context.client_info.get("device_id")

    user_sessions = MemberSession(
        is_active=True,
        user_id=member.id,
        device_id=device_id,
        ip_address=app_context.request.ip,
    )

    db.add(user_sessions)
    db.commit()
    db.refresh(user_sessions)

    user_login_info_id = _Security.short_encode(user_sessions.id)

    # Session
    app_context.setting.setting_session["MASTER_KEY"] = (
        f"{member.secret}///{user_login_info_id}"
    )
    app_context.setting.setting_session["id"] = _Security.short_encode(member.id)

    timestamp = TimeStamp.now_timestamp()

    try:
        loginfo = _Security.dict_decode(member.loginfo)
    except Exception:
        loginfo = {}

    loginfo[timestamp] = user_login_info_id
    member.loginfo = _Security.dict_encode(loginfo)

    # Device list update
    device = list(member.device)
    if user_login_info_id not in device:
        device.append(user_login_info_id)

    member.device = device

    # Save member changes
    db.merge(member)
    db.flush()
    db.commit()
    db.refresh(member)

    # Cache
    MemberCache._cache(member)
    app_context.setting.update_cookie()

    try:
        del app_context.response["email"]
        del app_context.response["password"]
    except:
        pass

    MetaData.redirect_url = get_query_value("redirect", "/")
    return
    # return "redirect"
