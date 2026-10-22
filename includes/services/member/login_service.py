from includes.schemas.cache.member import MemberCache
from includes.src.request import Request
from sqlalchemy import inspect


from includes.database.models.utils import TimeStamp
from includes.core.security import _Security
from includes.database.models.primary import Members, MemberSession


async def complete_login(member: Members, db, request: Request = None) -> str | None:

    device_id = request.state.client_info.get("device_id")

    user_sessions = MemberSession(
        is_active=True,
        user_id=member.id,
        device_id=device_id,
        ip_address=request.ip,
    )

    db.add(user_sessions)
    db.commit()
    db.refresh(user_sessions)

    user_login_info_id = _Security.short_encode(user_sessions.id)

    # Session
    request.state.setting.setting_session["MASTER_KEY"] = (
        f"{member.secret}///{user_login_info_id}"
    )
    request.state.setting.setting_session["id"] = _Security.short_encode(member.id)

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
    await MemberCache._cache(member)
    request.state.setting.update_cookie()

    try:
        del request.state.response["email"]
        del request.state.response["password"]
    except:
        pass

    request.state.metadata.redirect_url = request.query_params.get(
        "redirect", "/?refresh=true"
    )
    return
    # return "redirect"
