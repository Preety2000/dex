from typing import Optional, Union
from sqlalchemy import or_, select
from includes.schemas.captcha import captcha_verification
from includes.utils._sub import configure_page
from includes.core.config import MASTER_KEY, app_context
from includes.database.connection import active_primary_db
from includes.database.dataclass.dataclass import serialize
from includes.database.models.owner import Members, MemberSession, VerifyIdentity
from includes.schemas.articles import ArticleService
from includes.schemas.cache.member import MemberCache
from includes.services.member.identity import Identity
from includes.services.member.login import Login
from includes.services.member.logout import LogoutHandler
from includes.services.member.signup import SineUp
from includes.core.security import _Security
from includes.utils.meb import (
    GENDER,
    format_session_info,
    extract_id_from_roll,
    serialize_member,
)
from includes.utils.utils import get_post_value, json_null_response, json_response
from includes.database.models.utils import TimeStamp


from typing import Union

from sqlalchemy import or_, select

def get_member(query: Union[str, int]):
    print("\033[91mget method call member get_member\033[0m")

    stmt = (
        select(Members)
        .where(
            or_(
                Members.id == query,
                Members.email == query,
                Members.phone == query,
                Members.secret == query,
            )
        )
        .limit(1)
    )

    session_member = app_context.db.execute(stmt).scalar_one_or_none()

    return (
        serialize_member(MemberCache._cache(session_member))
        if session_member
        else None
    )



def filter_member_by_device(member: dict, device_key: str) -> dict:
    # print(member, device_key)
    return member if device_key in member.get("device", []) else {}


async def update_member_profile_image(user_id: int, file_name: str):
    db_session = await active_primary_db()

    member = db_session.query(Members).filter(Members.id == user_id).first()

    encoded_name = _Security.short_encode(file_name)
    member.image_src = encoded_name
    db_session.commit()
    db_session.refresh(member)
    await MemberCache._cache(member)
    return True


async def getrollnumber(rollnumber: int):
    userid = extract_id_from_roll(rollnumber)
    record = await MemberCache.get_with_id(userid)
    return serialize(record)


class ClassUser:

    async def identifier(self, member):
        db_session = await active_primary_db()
        session_member = (
            db_session.query(Members)
            .filter(
                or_(
                    Members.phone == member,
                    Members.email == member,
                    Members.username == member,
                )
            )
            .first()
        )

        return session_member

    async def teacher(self, member):
        db_session = await active_primary_db()
        return


    async def getrollnumber(self, rollnumber: int):
        userid = extract_id_from_roll(rollnumber)
        record = await MemberCache.get_with_id(userid)
        return serialize(record)

    async def update(self, id_or_email, option):
        db_session = await active_primary_db()

        try:
            member_id = int(id_or_email)
            stmt = select(Members).where(Members.id == member_id)
        except (TypeError, ValueError):
            stmt = select(Members).where(Members.email == id_or_email)

        result = db_session.execute(stmt)
        member = result.scalar_one_or_none()

        if not member:
            return None

        for name, value in option.items():
            if name == "gender" and value in GENDER:
                value = GENDER.index(value)

            if value is not None:
                setattr(member, name, value)

        db_session.commit()
        await MemberCache._cache(member)

        return member

    async def check_user_name(self, username):
        db_session = await active_primary_db()
        query = db_session.query(Members).filter_by(username=username).first()
        return query

    async def password_verify(self, email, password):
        db_session = await active_primary_db()
        member = db_session.query(Members).filter_by(email=email).first()

        return True if member and member.check_password(password) else None

    async def apimapp(self, query):

        member = await app_context.setting.member()
        if member and query == "edit":

            query = {
                field: await get_post_value(field)
                for field in (
                    "email",
                    "username",
                    "name",
                    "gender",
                    "website",
                    "biography",
                )
            }

            if not await captcha_verification():
                return json_null_response(
                    code="Ex000042",
                    details=[
                        "captcha_virification_error",
                        app_context.function.utc("Captcha not verified!"),
                    ],
                )

            get_username = await self.check_user_name(query["username"])
            if get_username and not get_username.email == query["email"]:
                return json_null_response(
                    details=["username", "This username is not available!"],
                    code="Ex000043",
                )

            if not member.get("email") == query["email"]:
                return json_null_response(
                    details=["session", "Session not found!"], code="Ex000044"
                )

            await self.update(member.get("id"), query)
            return json_response(
                [
                    {"update": query},
                    200,
                    {"message": "Your profile updated successfully!"},
                ]
            )

        if member and query == "query":
            info = {
                item: member[item]
                for item in [
                    "biography",
                    "gender",
                    "name",
                    "username",
                    "email",
                    "img",
                    "role",
                ]
            }
            return json_response([{"auth_session": info, "fatching_key": None}, 200])

        if member and query == "password_verify":

            email = await get_post_value("email")
            password = await get_post_value("password")

            if not await captcha_verification():
                return json_null_response(
                    details=[
                        "captcha_virification_error",
                        app_context.function.utc("Captcha not verified!"),
                    ],
                    code="Ex000042",
                )

            verify = await self.password_verify(email, password)
            if member.get("email") == email and verify:
                return json_response(
                    [
                        {"verify": True},
                        200,
                        {"message": "Password verification successful 😘!"},
                    ]
                )

            return json_null_response(
                details={"message": "Password verification failed 😌!"}, code="Ex000048"
            )

        return [{"ff": query}]

    async def logout(self):
        return await LogoutHandler.process_logout()

    def forgot_password(self, chacks=False):
        template = "member/forgot_password.html"
        inputOption = [
            "name",
            "email",
            # "mobile",
            "password",
            "cpassword",
        ]
        app_context.response["forgot_password"] = {}
        for inputs in inputOption:
            inputsValue = app_context.request.post(inputs)
            app_context.response["forgot_password"][inputs] = inputsValue

            if not inputsValue:
                app_context.response["forgot_password"][inputs + "_error"] = "error"
                chacks = True

        if chacks == True:
            return template

    @classmethod
    async def get_template(cls, template=None):
        self = cls()
        reso = app_context.route.resource_type.replace(".php", "")

        if reso == "login":
            return await Login.authenticate()

        if reso == "signup":
            return await SineUp.authenticate()

        member = await app_context.setting.member()

        if reso == "teacher" and app_context.route.resource_slug == "verify-indentity":
            return await Identity.teacher_verify_identity()

        if app_context.function.is_post():
            return await getattr(self, reso)(member) or "error"

        elif reso == "password" and app_context.route.resource_slug == "reset":
            configure_page(
                template=template if template else "member/forgot_password",
                title="Reset Password",
                suffix=True,
            )

            template = template if template else "member/forgot_password"

        template = (
            template
            if template
            else "query/error" if member or reso == "signup" else "query/login_required"
        )

        return template

    @staticmethod
    async def liked_questions():
        system_user = await app_context.setting.member()
        if not system_user:
            configure_page(
                template="query/login_required", title="Login Required", suffix=True
            )
            return {}

        article = await ArticleService.find_liked_article(system_user.get("id"))
        configure_page(
            template="member/liked-question", title="Liked Question", suffix=True
        )
        return {"data_querys": article}

    @staticmethod
    async def fetch_active_sessions(fetch_all: bool = False):
        """User ke devices/sessions fetch karta hai.
        :param fetch_all: True hone par user ke saare sessions lata hai,
        False hone par sirf current/active device sessions.
        """
        system_user = await app_context.setting.member()

        # Validation checks
        if not system_user or not system_user.get("device"):
            return {
                "session_error": True,
                "message": "Invalid or expired session. Please login again.",
            }

        # Decode session keys safely
        session_ids = []
        for device_key in system_user["device"]:
            try:
                decoded_id = int(_Security.short_decode(device_key))
                session_ids.append(decoded_id)
            except Exception:
                continue

        if not session_ids and not fetch_all:
            return []

        db = await active_primary_db()

        # SQLAlchemy Query Execution
        # If fetch_all is True: fetch all sessions for the user
        # If fetch_all is False: fetch sessions matching decoded session_ids
        stmt = select(MemberSession).where(
            MemberSession.user_id == system_user["id"]
            if fetch_all
            else MemberSession.id.in_(session_ids)
        )

        # SQLAlchemy Async execution
        query_result = db.execute(stmt)
        records = query_result.scalars().all()

        # Format and return device info
        return [await format_session_info(record, session_ids) for record in records]
