from email.mime import image
import os
import math
import posixpath
import fitz
import aiofiles
import mimetypes
from io import BytesIO
from pathlib import Path
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont
from fastapi import HTTPException, Request, Response
from fastapi.responses import (
    FileResponse,
    JSONResponse,
    StreamingResponse,
)

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

from includes.api.router import DynamicSokitURLRoute
from includes.core.globals.route_context import Route
from includes.core.security import _Security
from includes.core.globals.entry import app_context
from includes.core.globals.coreutils import process_image

from includes.core.repo.dir_manager import folder
from includes.core.repo.author import _FileAuthor
from includes.core.repo.upload import FileUpload
from includes.core.repo.thumbnail import Thumbnail
from includes.core.repo.db_media import MediaManager

from includes.schemas.cache.member import MemberCache

from includes.utils.file import get_paginated_files
from includes.utils.meb import get_email_folder_info
from includes.utils.utils import get_query_num

# =========================================================
# SVG TO PNG
# =========================================================


def svg_to_png_bytesio(svg_path: str, width=None, height=None):
    drawing = svg2rlg(svg_path)

    if width and height:
        scale_x = width / drawing.width
        scale_y = height / drawing.height
        drawing.scale(scale_x, scale_y)

    png_data = renderPM.drawToString(drawing, fmt="PNG")
    return BytesIO(png_data)


# =========================================================
# VIDEO RESPONSE
# =========================================================


def video(folder_path, filename):
    file_path = posixpath.join(folder_path, filename)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=filename,
        headers={"Cache-Control": "public, max-age=31536000"},
    )


# =========================================================
# FILE CLASS
# =========================================================


class Media:
    directories = {
        "images": folder.image_folder,
        "svg": folder.svg_folder,
        "pdf": folder.pdf_folder,
        "video": folder.video_folder,
        "audio": folder.audio_folder,
    }

    def __init__(self, request):
        self.request = request

        # Create folders
        for _, path in self.directories.items():
            os.makedirs(path, exist_ok=True)

    # FILE SIZE
    def get_file_size(self, file_path):

        size_bytes = os.stat(file_path).st_size

        if size_bytes == 0:
            return 0, "0B"

        size_name = ("B", "KB", "MB", "GB")

        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)

        s = round(size_bytes / p, 2)

        return size_bytes, f"{s} {size_name[i]}"

    # IMAGE DIMENSIONS
    def get_image_dimensions(self, file_path):

        try:
            with Image.open(file_path) as img:
                return img.width, img.height

        except Exception:
            return None, None

    # SVG FILES
    @staticmethod
    def get_svg_files(folder_path):

        svg_files_data = {}

        for file in os.listdir(folder_path):

            if file.endswith(".svg"):

                file_path = posixpath.join(folder_path, file)

                with open(file_path, "r", encoding="utf-8") as svg_file:
                    file_content = svg_file.read()

                svg_files_data[file.replace(".svg", "")] = file_content

        return svg_files_data

    # UPLOAD FILE
    async def save_upload_file(self, file, file_path):

        async with aiofiles.open(file_path, "wb") as f:

            while chunk := await file.read(1024 * 1024):
                await f.write(chunk)

    # THUMBNAIL CREATOR
    def create_thumbnail_file(self, file_path, save_path):

        mime_type, _ = mimetypes.guess_type(file_path)

        try:

            if mime_type == "application/pdf":

                pdf_document = fitz.open(file_path)

                page = pdf_document.load_page(0)

                mat = fitz.Matrix(0.3, 0.3)

                pix = page.get_pixmap(matrix=mat)

                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            elif mime_type.startswith("image"):

                image = Image.open(file_path)

            elif mime_type.startswith("audio"):

                svgfile = posixpath.join(folder.static_svg, "audio.svg")

                buffered = svg_to_png_bytesio(svgfile)

                image = Image.open(buffered)

            else:
                return

            image.thumbnail((300, 300))

            image.save(save_path, format="WEBP", quality=80, optimize=True)

        except Exception as e:
            print("Thumbnail Error:", e)

    # FILE SENDER
    def file_sender(self, file_path):

        if not os.path.exists(file_path):
            raise HTTPException(404, "File not found")

        print(file_path)

        mime_type, _ = mimetypes.guess_type(file_path)

        headers = {"Cache-Control": "public, max-age=31536000"}

        return FileResponse(file_path, media_type=mime_type, headers=headers)

    # SVG GETTER
    def get_svg(self, filename):

        filename = filename.replace(".svg", "")

        if filename == "m=v2":

            icons_lists = self.request.query_params.getlist("icon")

            if len(icons_lists) > 0:

                icon_lists = {
                    icon: app_context.svg_lists[icon]
                    for icon in icons_lists
                    if icon in app_context.svg_lists
                }

                return JSONResponse(content=icon_lists)

            return JSONResponse(content=app_context.svg_lists)

        if filename in app_context.svg_lists:

            svg_content = app_context.svg_lists[filename]

            return Response(content=svg_content, media_type="image/svg+xml")

    # GET
    async def execute(self, request: Request = None, route: Route = None):

        if route.section == "upload":
            return await FileUpload.execute(request)

        # SVG
        if route.section == "svg" and route.scope:
            path = route.scope
            if route.entity:
                path = posixpath.join(route.scope, route.entity)

            return self.get_svg(route.scope)

        # IMAGE
        if route.section == "img":
            if route.scope == "category":
                route.entity = route.entity or "empty.webp"
            if route.entity:
                route.scope = posixpath.join(route.scope, route.entity)

            return await process_image(f"img/{route.scope}", "img")

        # ICon
        if route.section == "icon":
            if route.entity:
                route.scope = posixpath.join(route.scope, route.entity)

            return await process_image(f"icon/{route.scope}", "img")

        # THUMBNAIL
        if route.section == "th":

            path = request.query_params.get("pt")

            file_path = _Security.short_decode(path)

            file_path = folder.root + file_path
            thumb_name = Path(file_path).name + ".webp"
            thumb_path = posixpath.join(folder.root, "thumbs", thumb_name)

            if not os.path.exists(thumb_path):
                self.create_thumbnail_file(file_path, thumb_path)

            return FileResponse(thumb_path, media_type="image/webp")

        # USER IMAGE
        if route.section == "u" and route.scope:

            roll_no, folder_path = get_email_folder_info(route.scope, False)
            file_path = posixpath.join(folder_path, "profile.webp")

            name = "*"
            if roll_no and not os.path.exists(file_path):
                try:
                    user_value = await MemberCache.get_with_id(roll_no)
                except:
                    user_value = {"name": "Error"}

                if user_value:
                    name = user_value["name"]

            image = (
                Image.open(file_path)
                if os.path.exists(file_path)
                else self.create_avatar_from_letter(name)
            )
            image.thumbnail((150, 150))
            img_io = BytesIO()

            image.save(img_io, format="WEBP", quality=80, optimize=True)

            img_io.seek(0)

            return StreamingResponse(img_io, media_type="image/webp")

        # FILES
        if not route.section:
            return ""

        if route.section == "exnr" and route.scope and route.entity:
            path = posixpath.join(
                folder.exnr,
                route.scope,
                route.entity,
            )
            if os.path.exists(path):
                return self.file_sender(path)
            return self.file_sender("/")

        upload_path = posixpath.join(folder.upload_folder, route.section)
        static_path = posixpath.join(folder.static_folder, route.section)

        if route.scope:
            upload_path = posixpath.join(upload_path, route.scope)
            static_path = posixpath.join(static_path, route.scope)

        if route.entity:
            upload_path = posixpath.join(upload_path, route.entity)
            static_path = posixpath.join(static_path, route.entity)

        if os.path.exists(upload_path):
            return self.file_sender(upload_path)

        if os.path.exists(static_path):
            return self.file_sender(static_path)

        raise HTTPException(404, f"File not found! {route}")

    # USER DEFAULT IMAGE
    def create_avatar_from_letter(self, string):
        colors = {
            "A": "#7A1F1B",
            "B": "#740F32",
            "C": "#4E1458",
            "D": "#341D5C",
            "E": "#1F285A",
            "F": "#104C7A",
            "G": "#027D7A",
            "H": "#005E6A",
            "I": "#004C44",
            "J": "#266226",
            "K": "#46621E",
            "L": "#666E1C",
            "M": "#806004",
            "N": "#7C4C00",
            "O": "#7A2B11",
            "P": "#3C2A24",
            "Q": "#303E44",
            "R": "#78304A",
            "S": "#5D3464",
            "T": "#3C4064",
            "U": "#325A7A",
            "V": "#026A70",
            "W": "#265A56",
            "X": "#40623C",
            "Y": "#6E703C",
            "Z": "#6A3A2A",
        }

        letter = string[0].upper()
        background_color = colors.get(letter, "#9E9E9E")

        # image = Image.new("RGB", (400, 400), background_color)
        # draw = ImageDraw.Draw(image)

        # try:
        #     font = ImageFont.truetype("arial.ttf", 240)
        # except Exception:
        #     font = ImageFont.load_default()

        # draw.text((120, 70), letter, fill="#FFFFFF", font=font)

        # return image

        image = Image.new("RGB", (400, 400), background_color)
        draw = ImageDraw.Draw(image)

        # Auto-fit font size
        max_width = 360
        max_height = 360

        font_size = 400

        while font_size > 10:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except Exception:
                font = ImageFont.load_default()
                break

            bbox = draw.textbbox((0, 0), letter, font=font)

            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            if text_width <= max_width and text_height <= max_height:
                break

            font_size -= 2

        # Center automatically
        bbox = draw.textbbox((0, 0), letter, font=font)

        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (400 - text_width) // 2 - bbox[0]
        y = (400 - text_height) // 2 - bbox[1]

        draw.text((x, y), letter, fill="#FFFFFF", font=font)

        return image

    # FILE METADATA
    def get_file_metadata(self, folder_path, file, filetype):

        file_path = posixpath.join(folder_path, file)

        stat = os.stat(file_path)

        size_bytes, file_size = self.get_file_size(file_path)

        width, height = self.get_image_dimensions(file_path)

        mime_type, _ = mimetypes.guess_type(file_path)

        file_mtime = datetime.fromtimestamp(stat.st_mtime).strftime(
            "%Y-%m-%dT%H:%M:%S%z"
        )

        thumbnail = Thumbnail.create(file_path=file_path, size=(2 * 1024))

        return {
            "src": f"/media/{filetype}/{file}",
            "id": file,
            "type": mime_type,
            "size": file_size,
            "size_bytes": size_bytes,
            "saveDate": file_mtime,
            "width": width or thumbnail["width"],
            "height": height or thumbnail["height"],
            "name": file,
            "thumbnail": thumbnail["data_url"],
        }

    # GET FILES
    def getfiles_with_path(self, folder_path, filetype):

        files = []

        for file in os.listdir(folder_path):
            files.append(self.get_file_metadata(folder_path, file, filetype))
        return files

    # LIBRARY

    async def library(self, action=None, request: Request = None):

        if action == "upload":
            return await FileUpload.execute(request)

        location = _FileAuthor(request).get("l")
        page = get_query_num(request.query_params, "page", 1)
        limit = get_query_num(request.query_params, "limit", 20)

        start = (page - 1) * limit
        end = start + limit

        path = request.query_params.get("path", request.state.roote.action)

        print("Library Path: and location", path, location)

        if path and path == "root-file" and "category" == location:
            directory_path = folder.ensure_directory(folder.static_img, "category")

        elif path and path != "media-files":
            directory_path = self.directories.get(path)

            if not directory_path:
                return {"error": "Invalid path"}

        else:
            for filetype, folder_path in self.directories.items():
                directory_path = folder_path

        print("directory_path", directory_path)
        paginated_files = get_paginated_files(directory_path, start=start, end=end)
        resolved_assets = await MediaManager.fetch_or_sync_assets(
            directory_path=directory_path,
            target_filenames=paginated_files.get("files", []),
        )

        paginated_files["files"] = resolved_assets
        return paginated_files
