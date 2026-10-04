import os
import random
import string

from io import BytesIO
from fastapi.responses import StreamingResponse
from includes.core.globals.fun import random_string
from includes.core.globals.entry import app_context
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime, timedelta
from includes.core.repo.schemas.msg import MsgPackHandler
from includes.core.repo.dir_manager import folder
from includes.utils.utils import get_post_value


def generate_captcha_text(length: int = 6) -> str:
    # Confusing characters ko hata diya
    characters = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
    return "".join(random.choice(characters) for _ in range(length))


def generate_cookie_value() -> str:
    return "Ent.5." + "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(40)
    )


class Captcha:
    def __init__(self, cookie):
        self.storage = None
        self.cookie = cookie
        self.name = "capvercs"
        self.session = MsgPackHandler(self.name)

    async def get(self, value=None):
        self.storage = await self.delete_expired_codes()
        return self.storage.get(self.cookie, value)

    async def verify(self, code):
        captcha_data = await self.get({})
        if not captcha_data:
            return False

        if captcha_data["code"] == code and captcha_data["max_age"] > int(
            datetime.now().timestamp()
        ):
            if self.cookie in self.storage:
                del self.storage[self.cookie]
                await self.session.save(self.storage)
            return True

        return False

    async def insert(self, code):
        current_time = datetime.now()
        after_10_minutes = current_time + timedelta(minutes=10)
        after_10_minutes_int = int(after_10_minutes.timestamp())
        self.storage = await self.delete_expired_codes()
        self.storage[self.cookie] = {"code": code, "max_age": after_10_minutes_int}
        await self.session.save(self.storage)

        return True

    async def delete_expired_codes(self):
        # Load the storage if not already loaded
        self.storage = self.storage or await self.session.get()

        # Get the current timestamp
        current_timestamp = int(datetime.now().timestamp())

        # Filter out any captcha codes that have expired (older than 10 minutes)
        self.storage = {
            key: value
            for key, value in self.storage.items()
            if value["max_age"] > current_timestamp
        }

        # Save the updated storage after deleting expired codes
        await self.session.save(self.storage)
        return self.storage

    async def delete(self, name):
        # Load the storage if not already loaded
        self.storage = await self.session.get()

        # Remove the captcha entry by name
        if self.cookie in self.storage:
            del self.storage[self.cookie]

        # Save the updated storage after deletion
        await self.session.save(self.storage)
        return self.storage

    async def update(self, code):
        return await self.insert(code)

    @staticmethod
    async def create() -> StreamingResponse | FileNotFoundError:
        width, height = 300, 100

        resource = generate_captcha_text(6)
        base_image = Image.new("RGB", (width, height), "#FFFFFF")
        draw = ImageDraw.Draw(base_image)

        # Font path
        font_path = folder._get_file_path("static", "font", "captcha.ttf")

        if not os.path.exists(font_path):
            raise FileNotFoundError(f"CAPTCHA font not found: {font_path}")

        font = ImageFont.truetype(font_path, 62)

        # Draw CAPTCHA characters
        x_start = 5

        for char in resource:
            x_offset = random.randint(-5, 5)
            y_offset = random.randint(-8, 8)
            angle = random.randint(-25, 25)

            char_color = (
                random.randint(0, 100),
                random.randint(0, 100),
                random.randint(0, 100),
            )

            char_image = Image.new("RGBA", (80, 80), (255, 255, 255, 0))
            char_draw = ImageDraw.Draw(char_image)

            # Center-ish placement
            char_draw.text((8, 0), char, font=font, fill=(*char_color, 255))
            char_image = char_image.rotate(
                angle,
                expand=True,
                resample=Image.Resampling.BICUBIC,
            )

            base_image.paste(
                char_image,
                (x_start + x_offset, 5 + y_offset),
                char_image,
            )

            x_start += 45

        # Noise points
        for _ in range(80):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)

            draw.point(
                (x, y),
                fill=(
                    random.randint(150, 255),
                    random.randint(150, 255),
                    random.randint(150, 255),
                ),
            )

        # Noise lines
        for _ in range(8):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)

            x2 = random.randint(0, width)
            y2 = random.randint(0, height)

            draw.line(
                (x1, y1, x2, y2),
                fill=(
                    random.randint(100, 200),
                    random.randint(100, 200),
                    random.randint(100, 200),
                ),
                width=2,
            )

        # Slight blur
        base_image = base_image.filter(ImageFilter.GaussianBlur(radius=0.7))

        # Convert image to memory
        image_io = BytesIO()
        base_image.save(image_io, format="WEBP", quality=90)
        image_io.seek(0)

        # Create new cookie if missing
        cookies = app_context.cookie.get("_cf_mt")
        if not cookies:
            cookies = "Ent.5." + random_string(40)
            app_context.cookie.insert("_cf_mt", cookies)

        # Save CAPTCHA
        captcha_storage = Captcha(cookies)
        await captcha_storage.insert(resource)

        # Response
        response = StreamingResponse(
            image_io,
            media_type="image/webp",
        )

        # Disable caching
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        return response


async def captcha_verification():
    form_data = await app_context.request.form()
    # captcha_code = form_data.get("captcha")
    captcha_code = await get_post_value("captcha")
    return True
    if not captcha_code:
        return False

    cookie_catutm = app_context.request.cookies.get("_cf_mt")
    if not cookie_catutm:
        return False

    captcha_storage = Captcha(cookie_catutm)
    return await captcha_storage.verify(captcha_code)
