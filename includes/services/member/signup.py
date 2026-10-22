import random
import string
from datetime import datetime

from sqlalchemy import func, select

from includes.src.request import Request
from database.username_list import USERNAME
from includes.schemas.captcha import captcha_verification
from includes.utils._sub import configure_page
from includes.core.config import main_database
from includes.core.dataclass.member import Gender
from includes.core.globals.entry import app_context
from includes.core.security import _Security
from includes.database.models.primary import Members
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
    async def authenticate(request: Request = None):

        error = False

        configure_page(
            request.state.metadata,
            template="member/signup_animation",
            title="Sign Up",
            suffix=True,
        )

        template = "member/signup_animation"
        # If not POST request
        if not request.is_post:
            return template

        # Collect & validate input
        for field in SineUp.input_fields:
            value = await get_post_value(
                request,
                field,
                "",
            )

            request.state.response[field] = value
            if not value:
                request.state.response[f"{field}_error"] = "error"
                error = True

        if error:
            return template

        # Password match check
        if request.state.response["password"] != request.state.response["cpassword"]:
            request.state.response["message"] = "Passwords do not match"
            return template

        # Captcha verification
        if not await captcha_verification(request=request):
            request.state.response["message"] = app_context.function.utc(
                "Captcha not verified!"
            )

            return template

        with main_database() as db:

            # Duplicate email check
            email_exists = db.execute(
                select(Members.id).where(
                    Members.email == request.state.response["email"]
                )
            ).scalar_one_or_none()

            if email_exists is not None:
                request.state.response["message"] = "Email already exists"
                return template

            # Duplicate mobile check
            mobile_exists = db.execute(
                select(Members.id).where(
                    Members.phone == request.state.response["mobile"]
                )
            ).scalar_one_or_none()

            if mobile_exists is not None:
                request.state.response["message"] = "Mobile number already exists"

                return template

            # Token generation
            token_xeper = _Security.short_encode(
                f"{request.state.response['name']}@"
                f"{request.state.response['email']}@"
                f"{request.state.response['mobile']}/"
                f"{request.ip}"
            )

            # Username generation
            username = SineUp.get_new_username(
                request.state.response["name"],
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
                name=request.state.response["name"],
                email=request.state.response["email"],
                phone=request.state.response["mobile"],
                gender=Gender.unspecified,
                ipinfo=request.ip,
                reg_no=reg_count + 1,
                secret=token_xeper[::-1],
                image_src="",
                biography="",
                device=[],
            )

            # Password hashing
            new_member.set_password(request.state.response["password"])

            db.add(new_member)
            db.commit()
            db.refresh(new_member)

            request.state.metadata.redirect_url = f"/success?token={token_xeper}"
            return await complete_login(new_member, db, request)

        return template
