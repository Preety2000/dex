from sqlalchemy import or_, select

from includes.src.request import Request
from includes.utils._sub import configure_page
from includes.core.config import main_database
from includes.core.globals.entry import app_context
from includes.database.models.primary import Members, MemberSession
from includes.utils.utils import get_post_value
from includes.services.member.logout import LogoutHandler
from includes.services.member.login_service import complete_login


class Login:
    MAX_DEVICES = 2

    def __init__(self, request: Request):
        self.request = request

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
    def log_failed_login(self, db, member, device_id):
        db.add(
            MemberSession(
                user_id=member.id, device_id=device_id, ip_address=self.request.ip
            )
        )

        db.commit()

    def create_logout_url(self, member, device_id):
        sep = "&" if "?" in self.request.full_path else "?"

        return (
            f"{self.request.full_path}" f"{sep}lq=true&nq={member.tk_id}&dv={device_id}"
        )

    async def login_for_token(self, access_token):
        logout = self.request.query_params.get("lq")

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

            return await complete_login(member, db, self.request)

    async def authenticate(self):
        configure_page(self.request.state.metadata, title="Login", suffix=True)

        # Device Logout Login
        login_token = self.request.query_params.get("nq")

        if login_token:
            return await self.login_for_token(login_token)

        template = "member/login"
        device_id = self.request.state.client_info.get("device_id")
        if not self.request.is_post:
            return template

        username = await get_post_value(self.request, "username", "")
        password = await get_post_value(self.request, "password", "")

        self.request.state.response.update(
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
        errors = Login.validate_credentials(username, password)
        if errors.get("username"):
            self.request.state.response["username_class"] = "error"

        if errors.get("password"):
            self.request.state.response["password_class"] = "error"

        if errors:
            return template

        with main_database() as db:

            member = Login.get_member(db, username)
            if not member:
                self.request.state.response["message_username"] = (
                    "Couldn’t find your account"
                )

                return template

            if not member.check_password(password):

                Login.log_failed_login(db, member, device_id)
                self.request.state.response["message_password"] = (
                    app_context.function.utc(
                        "Wrong password. Try again or click "
                        "Forgot password to reset it."
                    )
                )

                return template

            # Device Limit Check
            if len(member.device) >= Login.MAX_DEVICES:

                logout_url = self.create_logout_url(member, device_id)
                self.request.state.metadata.redirect_url = None
                msg_template = app_context.function.utc(
                    "This account is already active on two "
                    "another device. Continuing will log you "
                    "out from all other devices. To continue "
                    "logging in, {start_tag}click here{end_tag}."
                )

                self.request.state.response.update(
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

            return await complete_login(member, db, self.request)
