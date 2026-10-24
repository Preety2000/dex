import re
import json
import random
import string
from attr import dataclass
from includes.src.request import Request
from fastapi.responses import StreamingResponse
from includes.api.chat.index import CHAIT
from includes.core.cache import AppCache
from includes.core.globals.initialize import initialize_database
from includes.core.globals.entry import app_context
from includes.api.exam.manager.manager import API_EXAM_MANAGER
from includes.api.exam.results.results_manager import API_RESULTS_MANAGER
from includes.core.globals.route_context import Route
from includes.schemas.cache.likes import Likes
from includes.schemas.cache.terms import TermsCache
from includes.schemas.objective import ClassObjective
from includes.services.member.member import ClassUser
from includes.schemas.conversation import Conversation
from includes.core.repo.media import Media
from includes.schemas.search import Search
from includes.database.models.secondary import Article
from PIL import Image, ImageDraw, ImageFont

from includes.utils.utils import (
    create_slug,
    get_post_value,
    json_null_response,
    json_response,
)
from includes.database.connection import db


@dataclass
class ApiRequestSession:
    path: str
    referer: str
    params: str


def object_to_binary(obj):
    json_str = json.dumps(obj)
    return json_str.encode("utf-8")


def parse_url(url):
    # Remove the protocol (e.g., https://) and split the URL at the first '/' after the domain
    # Get the part after the domain
    path = url.split("//")[-1].split("/", 1)[-1]
    # Split the path into parts
    parts = path.split("/")
    # Map parts to the desired structure
    return {
        "resource_type": parts[0] if len(parts) > 0 else None,
        "resource_slug": parts[1] if len(parts) > 1 else None,
        "sub_action": parts[2] if len(parts) > 2 else None,
    }


# Function to generate random CAPTCHA text
def generate_captcha_text(length=6):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))


# Function to create CAPTCHA image
def create_captcha_image(captcha_text):
    width, height = 200, 60
    image = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Load a font (adjust path as necessary)
    font = ImageFont.load_default()

    # Draw the text on the image
    text_width, text_height = draw.textsize(captcha_text, font=font)
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    draw.text((text_x, text_y), captcha_text, fill=(0, 0, 0), font=font)

    # Add noise (optional)
    for _ in range(300):
        x, y = random.randint(0, width), random.randint(0, height)
        draw.point(
            (x, y),
            fill=(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            ),
        )

    return image


from langdetect import detect
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source="auto", target="en")


class API:
    def __init__(self, request):
        self.request = request

    def translate(self, text):
        error = False
        try:
            text = translator.translate(text)
        except:
            error = True

        return text, error

    async def index(self, request: Request = None, roots: Route = None):
        member = ClassUser(self.request)
        await initialize_database(request)

        entity = request.state.roote.entity
        action = request.state.roote.action

        if entity == "auth" and action == "t":
            examManager = API_EXAM_MANAGER(request=request)
            return await examManager.test_manager()

        if entity == "auth" and action == "r":
            manager = API_RESULTS_MANAGER(request=request)
            return await manager.result_manager()

        if entity == "conversations":
            message = await Conversation(request=request).index()
            return StreamingResponse(message, media_type="text/event-stream")

        if entity == "search":
            search = Search(self.request)
            searchs = await search.list()
            return json_response([{"searchs": searchs, "fatching_key": None}, 200])

        if entity == "profile":
            entity = await member.apimapp(action)
            return entity

        if entity == "feedback":
            member = await request.state.setting.member()
            if not member:
                return json_null_response(
                    code="Xe022524",
                    details="You must be loogged in to like this Artical.",
                )

            # Get the referer URL
            referer = self.request.headers.get("referer")
            referer = parse_url(referer)
            det_ = referer["resource_type"]
            res_ = referer["resource_slug"]
            sub_ = referer["sub_action"]

            log_ = await get_post_value(request, "log_")
            opg_ = await get_post_value(request, "opg_")

            category = await TermsCache.get_by_slug(det_)
            article = db.query(Article).filter(Article.slug == res_).first()
            if category and article and article.parameter == category.id:
                return await Likes.handle_like(
                    article_id=article.id,
                    users_id=member.get("id"),
                    option=("removelike" if len(opg_) == 20 else "like"),
                )

        if "practice" == entity and action:
            id = await get_post_value(request, "id")
            id = id.replace("F", "")

            query = await ClassObjective.get(id=int(id), request=request)
            if query:
                return json_response(
                    [
                        {
                            "excerpt": query.get("excerpt"),
                            "title": query.get("question"),
                        },
                        200,
                    ]
                )

        if entity == "setting" and action == "accept-cookie":

            request.state.cookie.insert(
                "_cf_bQ", "wgYeZFCqhmoLPRNXsSoFllKWYmUBrT", 3600 * 24 * 360
            )
            return json_response([{"accept": True}, 200])

        if entity == "logout":
            response = await member.logout()
            return json_response(response)

        if entity == "translate":
            text = await get_post_value(request, "q")
            translatedText, error = self.translate(text)
            translatedText = create_slug(translatedText)

            return json_response(translatedText)

        if entity == "media":
            media = Media(self.request)
            return await media.library(action, request)

        def detect_input_type(user_input):
            email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            phone_pattern = r"^\+?\d{7,15}$"

            if re.match(email_pattern, user_input):
                return "email"
            elif re.match(phone_pattern, user_input):
                return "phone"
            else:
                return "username"

        def not_found_message(user_input):
            input_type = detect_input_type(user_input)

            if input_type == "email":
                return f"No account found with the email: {user_input}."
            elif input_type == "phone":
                return f"No account found with the phone number: {user_input}."
            else:
                return f"No account found with the username: {user_input}."

        if entity == "account":
            requests_path = request.state.referer.path
            if requests_path == "/ut/accounts/password/reset":
                request_ip = getattr(request, "ip", None)

                if not request_ip:
                    return json_response(
                        {
                            "message": "Unable to verify client IP address. Please try again."
                        },
                        success=False,
                    )

                identifier = await get_post_value(request, "identifier")
                if not identifier:
                    return json_response(
                        {"message": "Please enter email, username, or phone number"},
                        success=False,
                    )

                request_ip_key = f"{request_ip}_{identifier}"
                if AppCache.created_at(request_ip_key):
                    return json_response(
                        {
                            "message": "Password reset link already sent. Please try again after 24 hours."
                        },
                        success=False,
                    )

                identifier_user = await member.identifier(identifier)
                if identifier_user and identifier_user.email:
                    name_part, domain_part = identifier_user.email.split("@", 1)
                    masked = f"{name_part[:2] + '*' * max(0, len(name_part) - 2)}@{domain_part}"

                    # Add IP to cache on success
                    AppCache.add(request_ip_key, True)

                    return json_response(
                        {
                            "message": f"An email with the password reset link has been sent to {masked}",
                            "ip": request_ip,
                        },
                        success=True,
                    )

                return json_response(
                    {"message": not_found_message(identifier)}, success=False
                )
        if entity == "chat":
            return await CHAIT.index()

        return [
            entity,
            action,
        ]
