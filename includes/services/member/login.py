from sqlalchemy import or_, select

from includes.utils._sub import configure_page
from includes.core.config import main_database
from includes.core.globals.entry import app_context
from includes.core.metadata import MetaData
from includes.database.models.owner import Members, MemberSession
from includes.utils.utils import get_post_value, get_query_value
from includes.services.member.logout import LogoutHandler
from includes.services.member.login_service import complete_login


class Login:
    MAX_DEVICES = 2

    @staticmethod
    def get_member(db, username: str):
        stmt = select(Members).where(
            or_(
                Members.username == username,
                Members.email == username,
            )
        )

        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def validate_credentials(
        username: str,
        password: str,
    ):
        errors = {}

        if not username:
            errors["username"] = True

        if not password:
            errors["password"] = True

        return errors

    @staticmethod
    def log_failed_login(
        db,
        member,
        device_id,
    ):
        db.add(
            MemberSession(
                user_id=member.id,
                device_id=device_id,
                ip_address=app_context.request.ip,
            )
        )

        db.commit()

    @staticmethod
    def create_logout_url(
        member,
        device_id,
    ):
        sep = "&" if "?" in app_context.request.full_path else "?"

        return (
            f"{app_context.request.full_path}"
            f"{sep}lq=true&nq={member.tk_id}&dv={device_id}"
        )

    @staticmethod
    async def login_for_token(access_token):
        logout = get_query_value("lq")

        if logout != "true" or not access_token:
            return None

        with main_database() as db:

            stmt = select(Members).where(Members.tk_id == access_token)

            member = db.execute(stmt).scalar_one_or_none()

            if not member:
                return None

            await LogoutHandler.logout_all_sessions(
                db,
                member.id,
            )

            member.device = []

            db.commit()

            return await complete_login(
                member,
                db,
            )

    @staticmethod
    async def authenticate():
        configure_page(
            title="Login",
            suffix=True,
        )

        # Device Logout Login
        login_token = get_query_value("nq")

        if login_token:
            return await Login.login_for_token(login_token)

        template = "member/login"

        device_id = app_context.client_info.get("device_id")

        if not app_context.function.is_post():
            return template

        username = await get_post_value(
            "username",
            "",
        )

        password = await get_post_value(
            "password",
            "",
        )

        app_context.response.update(
            {
                "email": username,
                "password": password,
                "message": "",
                "message_username": "",
                "message_password": "",
                "username_class": "",
                "password_class": "",
            }
        )

        # Validation
        errors = Login.validate_credentials(
            username,
            password,
        )

        if errors.get("username"):
            app_context.response["username_class"] = "error"

        if errors.get("password"):
            app_context.response["password_class"] = "error"

        if errors:
            return template

        with main_database() as db:

            member = Login.get_member(
                db,
                username,
            )

            if not member:
                app_context.response["message_username"] = "Couldn’t find your account"

                return template

            if not member.check_password(password):

                Login.log_failed_login(
                    db,
                    member,
                    device_id,
                )

                app_context.response["message_password"] = app_context.function.utc(
                    "Wrong password. Try again or click " "Forgot password to reset it."
                )

                return template

            # Device Limit Check
            if len(member.device) >= Login.MAX_DEVICES:

                logout_url = Login.create_logout_url(
                    member,
                    device_id,
                )

                MetaData.redirect_url = None

                msg_template = app_context.function.utc(
                    "This account is already active on two "
                    "another device. Continuing will log you "
                    "out from all other devices. To continue "
                    "logging in, {start_tag}click here{end_tag}."
                )

                app_context.response.update(
                    {
                        "email": "",
                        "password": "",
                        "message": msg_template.format(
                            start_tag=f"<a href='{logout_url}'>",
                            end_tag="</a>",
                        ),
                    }
                )

                return template

            return await complete_login(
                member,
                db,
            )
