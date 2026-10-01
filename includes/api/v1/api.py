import re
import json
import random
import string
from attr import dataclass
from fastapi.responses import StreamingResponse
from includes.api.chat.index import CHAIT
from includes.core.cache import AppCache
from includes.core.globals.initialize import initialize_database
from includes.core.globals.entry import app_context
from includes.api.exam.manager.manager import API_EXAM_MANAGER
from includes.api.exam.results.results_manager import API_RESULTS_MANAGER
from includes.schemas.cache.likes import Likes
from includes.schemas.cache.terms import TermsCache
from includes.schemas.objective import ClassObjective
from includes.services.member.member import ClassUser
from includes.schemas.conversation import Conversation
from includes.core.repo.media import Media
from includes.schemas.search import Search
from includes.db.models.secondary import Article
from PIL import Image, ImageDraw, ImageFont

from includes.utils.utils import get_post_value, json_response


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


from deep_translator import GoogleTranslator
from langdetect import detect


class API:
    def __init__(self, request):
        self.request = request

    def translate(self, text):
        error = False
        try:
            text = GoogleTranslator(source="auto", target="es").translate(text)

        except:
            error = True

        return text, error
        return json_response(text)

    async def index(self):
        # scope_type/scope_slug/resource_type/resource_slug/sub_action/child_entity/modifier

        member = ClassUser()
        await initialize_database()

        resource_type = app_context.route.resource_type
        resource_slug = app_context.route.resource_slug

        if resource_type == "auth" and resource_slug == "t":
            examManager = API_EXAM_MANAGER()
            return await examManager.test_manager()

        if resource_type == "auth" and resource_slug == "r":
            manager = API_RESULTS_MANAGER()
            return await manager.result_manager()

        if resource_type == "conversations":
            message = await Conversation.index()
            return StreamingResponse(message, media_type="text/event-stream")

        if resource_type == "search":
            search = Search(self.request)
            searchs = await search.list()
            return json_response([{"searchs": searchs, "fatching_key": None}, 200])

        if resource_type == "profile":
            resource_type = await member.apimapp(resource_slug)
            return resource_type

        if resource_type == "feedback":
            member = await app_context.setting.member()
            if not member:
                return json_response([{"message": "You must be loogged in to like this Artical."}])

            # Get the referer URL
            referer = self.request.headers.get("referer")
            referer = parse_url(referer)
            det_ = referer["resource_type"]
            res_ = referer["resource_slug"]
            sub_ = referer["sub_action"]

            log_ = await get_post_value("log_")
            opg_ = await get_post_value("opg_")

            category = await TermsCache.get_by_slug(det_)
            article = app_context.db.query(Article).filter(Article.slug == res_).first()
            if category and article and article.parameter == category.id:
                return Likes.handle_like(
                    article_id=article.id,
                    users_id=member.get("id"),
                    option=("removelike" if len(opg_) == 20 else "like"),
                )

        if "practice" == resource_type and resource_slug:
            id = await get_post_value("id")
            id = id.replace("F", "")

            query = await ClassObjective.get(id=int(id))
            if query:
                return json_response(
                    [
                        {"excerpt": query.get("excerpt"), "title": query.get("question")},
                        200,
                    ]
                )

        if resource_type == "setting" and resource_slug == "accept-cookie":

            app_context.cookie.insert(
                "_cf_bQ", "wgYeZFCqhmoLPRNXsSoFllKWYmUBrT", 3600 * 24 * 360
            )
            return json_response([{"accept": True}, 200])

        if resource_type == "logout":
            response = await member.logout()
            return json_response(response)

        if resource_type == "translate":
            text = await get_post_value("q")
            translatedText, error = self.translate(text)
            translatedText = translatedText.replace(" ", "-").lower()

            return json_response(translatedText)

        if resource_type == "media":
            media = Media(self.request)
            return await media.library(resource_slug, resource_type)

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

        if resource_type == "account":
            requests_path = app_context.request.referer.path
            if requests_path == "/ut/accounts/password/reset":
                request_ip = getattr(app_context.request, "ip", None)

                if not request_ip:
                    return json_response(
                        {
                            "message": "Unable to verify client IP address. Please try again."
                        },
                        success=False,
                    )

                identifier = await get_post_value("identifier")
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
        if resource_type == "chat":
            return await CHAIT.index()

        return [
            resource_type,
            resource_slug,
            app_context.route.sub_action,
        ]
