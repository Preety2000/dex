import random
import string
from datetime import datetime

from sqlalchemy import func, select

from database.username_list import USERNAME
from includes.schemas.captcha import captcha_verification
from includes.utils._sub import configure_page
from includes.core.config import main_database
from includes.core.dataclass.member import Gender
from includes.core.globals.fun import random_string
from includes.core.globals.entry import app_context
from includes.core.metadata import MetaData
from includes.core.security import _Security
from includes.db.models.owner import Members
from includes.services.member.login_service import complete_login
from includes.utils.utils import get_post_value


class SineUp:

    input_fields = [
        "name",
        "email",
        "mobile",
        "password",
        "cpassword",
    ]

    # Username Generator (Unique)
    @staticmethod
    def get_new_username(base_username: str, db, model):
        base_username = "".join(base_username.lower().split())
        base_username = "".join(ch for ch in base_username if ch.isalnum())

        username = base_username
        # Ensure uniqueness
        while True:
            exists = db.execute(
                select(model.id).where(model.username == username)
            ).scalar_one_or_none()

            if username not in USERNAME and exists is None:
                break

            suffix = "".join(
                random.choices(
                    string.digits,
                    k=3,
                )
            )
            username = f"{base_username}{suffix}"

        return username

    # Signup / Authentication
    @staticmethod
    async def authenticate():

        error = False

        configure_page(
            template="member/signup_animation",
            title="Sign Up",
            suffix=True,
        )

        template = "member/signup_animation"
        # If not POST request
        if not app_context.function.is_post():
            return template

        # Collect & validate input
        for field in SineUp.input_fields:
            value = await get_post_value(
                field,
                "",
            )

            app_context.response[field] = value
            if not value:
                app_context.response[f"{field}_error"] = "error"
                error = True

        if error:
            return template

        # Password match check
        if app_context.response["password"] != app_context.response["cpassword"]:
            app_context.response["message"] = "Passwords do not match"
            return template

        # Captcha verification
        if not await captcha_verification():
            app_context.response["message"] = app_context.function.utc(
                "Captcha not verified!"
            )

            return template

        with main_database() as db:

            # Duplicate email check
            email_exists = db.execute(
                select(Members.id).where(Members.email == app_context.response["email"])
            ).scalar_one_or_none()

            if email_exists is not None:
                app_context.response["message"] = "Email already exists"
                return template

            # Duplicate mobile check
            mobile_exists = db.execute(
                select(Members.id).where(
                    Members.phone == app_context.response["mobile"]
                )
            ).scalar_one_or_none()

            if mobile_exists is not None:
                app_context.response["message"] = "Mobile number already exists"

                return template

            # Token generation
            token_xeper = _Security.short_encode(
                f"{app_context.response['name']}@"
                f"{app_context.response['email']}@"
                f"{app_context.response['mobile']}/"
                f"{app_context.request.ip}"
            )

            # Username generation
            username = SineUp.get_new_username(
                app_context.response["name"],
                db,
                Members,
            )

            # Year-wise registration no
            current_year = datetime.now().year

            start = datetime(
                current_year,
                1,
                1,
            )

            end = datetime(
                current_year + 1,
                1,
                1,
            )

            reg_count = db.execute(
                select(func.count(Members.id)).where(
                    Members.timestamp >= start,
                    Members.timestamp < end,
                )
            ).scalar_one()

            # Create new member
            new_member = Members(
                username=username,
                name=app_context.response["name"],
                email=app_context.response["email"],
                phone=app_context.response["mobile"],
                gender=Gender.unspecified,
                ipinfo=app_context.request.ip,
                reg_no=reg_count + 1,
                secret=token_xeper[::-1],
                image_src="",
                biography="",
                device=[],
            )

            # Password hashing
            new_member.set_password(app_context.response["password"])

            db.add(new_member)
            db.commit()
            db.refresh(new_member)

            MetaData.redirect_url = f"/success?token={token_xeper}"

            return complete_login(
                new_member,
                db,
            )

        return template
