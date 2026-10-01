import os
import math
import fitz
import aiofiles
import mimetypes
from io import BytesIO
from pathlib import Path
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont
from fastapi import HTTPException, Response
from fastapi.responses import (
    FileResponse,
    JSONResponse,
    StreamingResponse,
)

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

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
from includes.utils.utils import get_query_value

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


def videos(folder_path, filename):
    file_path = os.path.join(folder_path, filename)

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
        "videos": folder.video_folder,
        "audios": folder.audio_folder,
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

                file_path = os.path.join(folder_path, file)

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

                svgfile = os.path.join(folder.static_svg, "audio.svg")

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
    async def execute(self, roots=None):
        # scope_type/scope_slug/resource_type/resource_slug/sub_action/child_entity/modifier

        if app_context.route.scope_slug == "upload":
            return await FileUpload.execute()

        # SVG
        if app_context.route.scope_slug == "svg":
            if app_context.route.resource_slug:
                app_context.route.resource_type = f"{app_context.route.resource_type}/{app_context.route.resource_slug}"

            return self.get_svg(app_context.route.resource_type)

        # ==============================
        # IMAGE
        # ==============================
        if app_context.route.scope_slug == "img":
            if app_context.route.resource_type == "category":
                app_context.route.resource_slug = (
                    app_context.route.resource_slug or "empty.png"
                )
            if app_context.route.resource_slug:
                app_context.route.resource_type = f"{app_context.route.resource_type}/{app_context.route.resource_slug}"
            return process_image(f"img/{app_context.route.resource_type}", "img")

        # ==============================
        # ICon
        # ==============================
        if app_context.route.scope_slug == "icon":
            if app_context.route.resource_slug:
                app_context.route.resource_type = f"{app_context.route.resource_type}/{app_context.route.resource_slug}"

            print(app_context.route.resource_type)
            return process_image(f"icon/{app_context.route.resource_type}", "img")

        # ==============================
        # THUMBNAIL
        # ==============================

        if app_context.route.scope_slug == "th":

            path = get_query_value("pt")

            file_path = _Security.short_decode(path)

            file_path = folder.root + file_path

            thumb_name = Path(file_path).name + ".webp"

            thumb_path = os.path.join(folder.root, "thumbs", thumb_name)

            if not os.path.exists(thumb_path):

                self.create_thumbnail_file(file_path, thumb_path)

            return FileResponse(thumb_path, media_type="image/webp")

        # ==============================
        # USER IMAGE
        # ==============================

        if app_context.route.scope_slug == "u" and app_context.route.resource_type:

            roll_no, folder_path = get_email_folder_info(
                app_context.route.resource_type, False
            )
            file_path = os.path.join(folder_path, "profile.webp")

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

        # ==============================
        # FILES
        # ==============================

        if not app_context.route.scope_slug:
            return ""

        if (
            app_context.route.scope_slug == "exnr"
            and app_context.route.resource_type
            and app_context.route.resource_slug
        ):
            path = os.path.join(
                folder.exnr,
                app_context.route.resource_type,
                app_context.route.resource_slug,
            )
            if os.path.exists(path):
                return self.file_sender(path)
            return self.file_sender("/")

        upload_path = os.path.join(folder.upload_folder, app_context.route.scope_slug)
        static_path = os.path.join(folder.static_folder, app_context.route.scope_slug)

        if app_context.route.resource_type:
            upload_path = os.path.join(upload_path, app_context.route.resource_type)
            static_path = os.path.join(static_path, app_context.route.resource_type)

        if app_context.route.resource_slug:
            upload_path = os.path.join(upload_path, app_context.route.resource_slug)
            static_path = os.path.join(static_path, app_context.route.resource_slug)

        if os.path.exists(upload_path):
            return self.file_sender(upload_path)

        if os.path.exists(static_path):
            return self.file_sender(static_path)

        raise HTTPException(404, f"File not found! {app_context.route}")

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

        image = Image.new("RGB", (400, 400), background_color)
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", 240)
        except Exception:
            font = ImageFont.load_default()

        draw.text((120, 70), letter, fill="#FFFFFF", font=font)

        return image

    # FILE METADATA
    def get_file_metadata(self, folder_path, file, filetype):

        file_path = os.path.join(folder_path, file)

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

    async def library(self, root=None):

        if app_context.route.scope_slug == "upload":
            return await FileUpload.execute()

        location = _FileAuthor.get("l")
        limit = int(get_query_value("limit") or 20)
        page = int(get_query_value("page") or 1)

        start = (page - 1) * limit
        end = start + limit

        path = get_query_value("path", app_context.route.scope_slug)

        print("Library Path:", path)

        if path and path == "root-file" and "category" == location:
            directory_path = folder.ensure_directory(folder.static_img, "category")

        elif path and path != "media-files":
            directory_path = self.directories.get(path)

            if not directory_path:
                return {"error": "Invalid path"}

        else:
            for filetype, folder_path in self.directories.items():
                directory_path = folder_path
                # files.extend(self.getfiles_with_path(folder_path, filetype))

        paginated_files = get_paginated_files(directory_path, start=start, end=end)
        resolved_assets = await MediaManager.fetch_or_sync_assets(
            directory_path=directory_path,
            target_filenames=paginated_files.get("files", []),
        )

        paginated_files["files"] = resolved_assets
        return paginated_files
