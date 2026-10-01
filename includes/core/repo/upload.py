import asyncio
import copy
import inspect
import os
import mimetypes
import re
import time
import fitz
from PIL import Image
from rembg import new_session, remove
from io import BytesIO
from pathlib import Path
from fastapi import UploadFile as FastAPIUploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile

from werkzeug.utils import secure_filename
from includes.core.globals.entry import app_context
from includes.core.security import _Security

from includes.services.member.identity import Identity
from includes.core.repo.dir_manager import folder
from includes.services.member.member import update_member_profile_image
from includes.core.repo.image_processor import ImageProcessor
from includes.utils.file import (
    build_file_upload_response,
    file_not_found,
    file_size_limit,
    get_file_metadata,
    image_crop_error,
    looks_like_signature,
    unsupported_file,
    valid_signature_message,
)
from includes.utils.meb import get_email_folder_info
from includes.utils.utils import get_query_value, json_response

ALLOWED_EXTENSIONS = {
    "images": {"png", "jpg", "jpeg", "gif"},
    "svg": {"svg"},
    "pdf": {"pdf"},
    "videos": {"mp4", "webm"},
    "audios": {"mp3", "mp4"},
}


def allowed_file(filename, filetype):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS[filetype]
    )


async def extract_uploaded_files(field_name: str | None = None):
    form = await app_context.request.form()
    files = {
        name: file
        for name, file in form.items()
        if isinstance(file, (FastAPIUploadFile, StarletteUploadFile))
    }

    return files.get(field_name) if field_name else files


class FileUpload:
    directories = {
        "images": folder.image_folder,
        "svg": folder.svg_folder,
        "pdf": folder.pdf_folder,
        "videos": folder.video_folder,
        "audios": folder.audio_folder,
    }

    allowed_extensions = {
        "images": {"jpg", "jpeg", "png", "gif", "webp", "bmp", "avif"},
        "svg": {"svg"},
        "pdf": {"pdf"},
        "videos": {"mp4", "webm", "mkv", "avi", "mov"},
        "audios": {"mp3", "wav", "ogg", "m4a", "aac", "flac"},
    }

    ALLOWED_IMAGE_EXTENSION: list = ["jpg", "png", "gif", "webp"]

    @staticmethod
    async def process_image_upload(
        *,
        file,
        upload_dir: str | Path,
        crop: bool | None = None,
        save_original: bool = True,
        max_file_size: int | None = None,
        output_filename: str | None = None,
        output_extensions: str = ".webp",
        resize: tuple[int | None, int | None] = (None, None),
        keep_aspect_ratio: bool = True,
        call_back: callable = None,
        metadata: dict | None = None,
    ):
        extensions = FileUpload.ALLOWED_IMAGE_EXTENSION

        # Validate content type
        allowed_types = {f"image/{ext}" for ext in extensions if ext != "jpg"}
        allowed_types.add("image/jpeg")

        if file.content_type not in allowed_types:
            return unsupported_file(file, extensions)

        # Read uploaded file
        content = await file.read()
        if max_file_size and len(content) > max_file_size:
            return file_size_limit(max_file_size)

        upload_dir = Path(upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        safe_name = secure_filename(file.filename)

        original_path = None
        processed_path = None

        # Save original file
        if save_original:
            original_path = upload_dir / safe_name
            with open(original_path, "wb") as fp:
                fp.write(content)

        # Process image with Pillow
        image = Image.open(BytesIO(content))

        # CROP PROCESSING LOGIC
        if crop is True:
            is_cropped, image = ImageProcessor.apply_crop(image)

        # RESIZE LOGIC
        width, height = resize
        if width or height:
            if keep_aspect_ratio:
                orig_width, orig_height = image.size
                if width and not height:
                    height = int(orig_height * (width / orig_width))
                elif height and not width:
                    width = int(orig_width * (height / orig_height))

                image.thumbnail((width, height), Image.Resampling.LANCZOS)
            else:
                if width and height:
                    image = image.resize((width, height), Image.Resampling.LANCZOS)

        # CALLBACK FUNCTION
        if callable(call_back):
            image = (
                await call_back(image)
                if inspect.iscoroutinefunction(call_back)
                else call_back(image)
            )

        # WEBP & FORMAT OPTIMIZATION
        filename = output_filename or Path(safe_name).stem
        filename = f"{filename}{output_extensions}"
        processed_path = upload_dir / filename
        save_format = output_extensions.replace(".", "").upper()

        if save_format in ("JPG", "JPEG"):
            save_format = "JPEG"
            if image.mode in ("RGBA", "LA", "P"):
                image = image.convert("RGB")
        elif save_format == "WEBP":
            if image.mode in ("P", "LA"):
                image = image.convert("RGBA")

        exif = ImageProcessor.build_exif_metadata(image, metadata)
        save_params = {
            "format": save_format,
            "quality": 80,
            "optimize": True,
            "exif": exif,
        }

        if save_format == "WEBP":
            save_params["method"] = 6

        image.save(processed_path, **save_params)

        return {
            "success": True,
            "file": file,
            "filename": filename,
            "original_path": str(original_path) if original_path else None,
            "processed_path": str(processed_path) if processed_path else None,
        }

    @staticmethod
    async def upload_profile_image():
        global folder

        active_member = await app_context.setting.member()
        decode_email, upload_dir = get_email_folder_info(active_member.get("id"), True)

        os.makedirs(upload_dir, exist_ok=True)

        file = await extract_uploaded_files("image")
        if not file:
            return file_not_found("image")

        data = await FileUpload.process_image_upload(
            file=file,
            crop=True,
            resize=(300, 300),
            save_original=True,
            upload_dir=upload_dir,
            output_filename="profile",
            output_extensions=".webp",
            max_file_size=5 * 1024 * 1024,
        )

        if data.get("success", None) is True:
            update_success = await update_member_profile_image(
                active_member.get("id"), file.filename
            )
            if update_success:
                return build_file_upload_response(
                    file, file.filename, f"/media/u/{decode_email}"
                )

        return json_response(None, message="Failed to update profile image")

    @staticmethod
    async def upload_examiner_image():
        global folder

        name = get_query_value("name")
        uid = get_query_value("key")
        user_dir = folder.ensure_directory(folder.exnr, uid)

        bind = None
        opexte = ".webp"
        resize = (280, 320)
        if name == "signature":
            opexte = ".png"
            resize = (300, 120)

            async def bind(image):
                session = new_session("isnet-general-use")
                image = remove(image, session=session)
                return image

        file = await extract_uploaded_files("image")
        if not file:
            return file_not_found("image")

        if name == "signature" and not await looks_like_signature(file):
            return valid_signature_message()

        data = await FileUpload.process_image_upload(
            file=file,
            resize=resize,
            save_original=False,
            upload_dir=user_dir,
            output_filename=name,
            output_extensions=opexte,
            max_file_size=5 * 1024 * 1024,
            call_back=bind,
        )

        if data.get("success", None) is True:
            return build_file_upload_response(
                file, data.get("filename"), f"/media/exnr/{uid}/{name}{opexte}"
            )

    @staticmethod
    async def upload_category_image():
        global folder

        name = get_query_value("name")
        category_dir = folder.ensure_directory(folder.static_img, "category")

        bind = None
        opexte = ".webp"

        file = await extract_uploaded_files("files")
        if not file:
            return file_not_found("files")

        data = await FileUpload.process_image_upload(
            file=file,
            save_original=False,
            upload_dir=category_dir,
            output_filename=name,
            output_extensions=opexte,
            max_file_size=5 * 1024 * 1024,
            call_back=bind,
        )

        try:
            if data.get("success", None) is True:
                return build_file_upload_response(
                    file, data.get("filename"), f"/media/img/category/{name}{opexte}"
                )
        except:
            return data

    @staticmethod
    async def upload_verify_indentity_document():
        global folder

        def pdf_to_icon(path, output):
            doc = fitz.open(path)

            try:
                if not doc.page_count:
                    return None

                pix = doc[0].get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
                # pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)

                pix.save(output)
                return output

            finally:
                doc.close()

        def is_valid_document(f):
            return bool(
                f
                and f.content_type in {"application/pdf", "image/jpeg", "image/png"}
                and re.search(r"\.(pdf|jpe?g|png)$", f.filename, re.I)
            )

        file = await extract_uploaded_files("file")
        return json_response(await Identity.save_verification_document(file))

        if not file:
            return {"error": "Please upload a valid PDF, JPG, or PNG document."}

        if not is_valid_document(file):
            return {"error": "Please upload a valid PDF, JPG, or PNG document."}

        uid = _Security.short_encode(await app_context.setting.member("id"))
        user_dir = folder.ensure_directory(folder.exnr, uid)

        # Save original document
        ext = os.path.splitext(file.filename)[1].lower()
        filename = secure_filename("ve_verification" + ext)
        filepath = os.path.join(user_dir, filename)
        file_bytes = await file.read()
        with open(filepath, "wb") as f:
            f.write(file_bytes)

        # Common preview/icon
        icon_name = "b95f30192536.png"
        icon_path = os.path.join(user_dir, icon_name)

        if file.content_type == "application/pdf":
            pdf_to_icon(filepath, icon_path)
        else:
            with open(icon_path, "wb") as f:
                f.write(file_bytes)

        return {
            "message": "Document uploaded successfully",
            "filename": filename,
            "icon": f"/media/exnr/{uid}/{icon_name}?t={int(time.time())}",
            "uri": f"/media/exnr/{uid}/{filename}",
        }

    async def process_upload(self, file):

        original_filename = file.filename.replace("#", "_")
        filename = secure_filename(original_filename)
        extension = filename.rsplit(".", 1)[-1].lower()

        for filetype, folder_path in self.array.items():

            if extension in ALLOWED_EXTENSIONS[filetype]:

                if not allowed_file(filename, filetype):
                    return {"error": "File type not allowed"}

                file_path = os.path.join(folder_path, filename)

                await self.save_upload_file(file, file_path)

                mime_type, _ = mimetypes.guess_type(file_path)

                # create thumbnail
                thumb_name = f"{filename}.webp"

                thumb_folder = os.path.join(folder.root, "thumbs")

                os.makedirs(thumb_folder, exist_ok=True)

                thumb_path = os.path.join(thumb_folder, thumb_name)

                if not os.path.exists(thumb_path):
                    self.create_thumbnail_file(file_path, thumb_path)

                filePath = file_path.replace(folder.root, "")

                short_encode = _Security.short_encode(filePath)

                return {
                    "url": f"/uploads/{filetype}/{filename}",
                    "name": filename,
                    "thumbnail": f"/media/th/img?pt={short_encode}",
                    "type": mime_type,
                }

        return {"error": "Invalid file"}

    @classmethod
    async def upload(cls, files):
        request = app_context.request

        if not files:
            return request.abort(400, "No file uploaded")

        result = {}

        for field, file in files.items():

            if not file or not file.filename:
                continue

            filename = secure_filename(file.filename)

            if not filename:
                return request.abort(400, "Invalid filename")

            ext = Path(filename).suffix.lower().lstrip(".")

            if not ext:
                return request.abort(415, "File extension is missing")

            # Extension ke basis par folder find karo
            file_type = next(
                (
                    folder_type
                    for folder_type, extensions in cls.allowed_extensions.items()
                    if ext in extensions
                ),
                None,
            )

            if file_type is None:
                return request.abort(415, f"Unsupported file type: .{ext}")

            # Folder mapping
            directory = cls.directories.get(file_type)

            if not directory:
                return request.abort(
                    500, f"Upload directory not configured: {file_type}"
                )

            # Folder nahi hai to create hoga
            os.makedirs(directory, exist_ok=True)

            file_path = os.path.join(directory, filename)

            try:
                # FastAPI / Starlette UploadFile ko chunk-wise save karo
                with open(file_path, "wb") as output:
                    while chunk := await file.read(1024 * 1024):
                        output.write(chunk)

            except (ConnectionError, BrokenPipeError, asyncio.CancelledError):
                # Client side r.abort() / disconnect
                if os.path.exists(file_path):
                    os.remove(file_path)

                raise

            except Exception:
                # Kisi bhi save error par incomplete file remove
                if os.path.exists(file_path):
                    os.remove(file_path)

                raise

            finally:
                await file.close()

            result[field] = {
                "filename": filename,
                "type": file_type,
                "extension": ext,
                "path": str(file_path),
                "size": getattr(file, "size", None),
            }

        if not result:
            return request.abort(400, "No valid file uploaded")

        return result

    @staticmethod
    async def execute():
        location = get_query_value("location")
        roots = {
            "examiner": FileUpload.upload_examiner_image,
            "category": FileUpload.upload_category_image,
            "profile_image": FileUpload.upload_profile_image,
            "verify_indentity": FileUpload.upload_verify_indentity_document,
        }

        callback = roots.get(location)
        if callable(callback):
            return await callback()

        uploaded_files = await extract_uploaded_files()

        return await FileUpload.upload(uploaded_files)
        # uploaded_files = await self.request.form()

        # files = uploaded_files.getlist("files")

        # results = await asyncio.gather(*(self.process_upload(file) for file in files))

        return {"uploaded_files": str(uploaded_files)}
