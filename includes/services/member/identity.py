import json
import os
import re
import time
import fitz
from sqlalchemy import MetaData
from dataclasses import dataclass, fields

from includes.core.globals.entry import app_context
from includes.db.connection import active_primary_db
from includes.db.models.owner import VerifyIdentity
from includes.schemas.cache.member import MemberCache
from includes.core.repo.dir_manager import folder
from werkzeug.utils import secure_filename

from includes.schemas.captcha import captcha_verification
from includes.utils.exm import get_folder_key
from includes.utils.file import get_files
from includes.utils.utils import get_post_value


@dataclass
class VerifyIdentityRequest:
    captcha: str = None
    subject: str = None
    experience: str = None
    document_name: str = None
    document_file: str = None


async def get_verify_identity_request(error):

    # ---------------- BUILD REQUEST ----------------
    request = VerifyIdentityRequest(
        **{
            f.name: await get_post_value(f.name)
            for f in fields(VerifyIdentityRequest)
            if f.name != "document_file"
        }
    )

    request.document_file = await get_files(
        name="document_file", ALLOWED_EXTENSIONS={"jpg", "jpeg", "png", "pdf"}
    )
    # ---------------- VALIDATION ----------------

    # Captcha empty check
    if not request.captcha:
        error["error_captcha"] = "Enter Captcha"

    # Captcha verify check
    elif not await captcha_verification():
        error["error_captcha"] = app_context.function.utc("Captcha not verified!")

    # Subject
    if not request.subject:
        error["error_subject"] = "Enter your Subject Name"

    # Experience
    if not request.experience:
        error["error_experience"] = "Enter your experience"

    # Document name
    if not request.document_name:
        error["error_document_name"] = "Enter document name"

    # ---------------- FILE VALIDATION ----------------
    ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}

    return request, error


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


class Identity:

    @staticmethod
    def is_valid_document(f):
        return bool(
            f
            and f.content_type in {"application/pdf", "image/jpeg", "image/png"}
            and re.search(r"\.(pdf|jpe?g|png)$", f.filename, re.I)
        )

    @classmethod
    async def save_verification_document(cls, file):
        global folder

        if not file or not cls.is_valid_document(file):
            return {"error": "Please upload a valid PDF, JPG, or PNG document."}

        user_id = await app_context.setting.member("id")
        if not user_id:
             return {"error": "Session not Active.. Error code Ex0025GH"}


        uid = get_folder_key(int(user_id))
        user_dir = folder.ensure_directory(folder.exnr, uid)

        ext = os.path.splitext(file.filename)[1].lower()
        filename = secure_filename("ve_verification" + ext)

        filepath = os.path.join(user_dir, filename)
        file_bytes = await file.read()

        with open(filepath, "wb") as f:
            f.write(file_bytes)

        # if not os.path.isfile(f):
        #     return {"error": "Uploaded file could not be saved."}

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

    @classmethod
    async def teacher_verify_identity(cls):
        global folder

        error = {}
        try_ = app_context.function.getRequestInt("try")
        app_context.response["error"] = error
        app_context.response["formView"] = True

        email = await app_context.setting.member("email")
        user_id = await app_context.setting.member("id")
        identity = await app_context.setting.member("identity")

        app_context.response["verify"] = identity

        # ---------------- helper ----------------
        async def set_verification_status(identity_data=None):
            app_context.response["formView"] = False

            if identity_data is None:
                q = await MemberCache.get_with_id(user_id)
                identity_data = q.get("identity")

            identity_data["try_number"] = len(identity_data.get("reject_message", []))
            identity_data["request_id"] = identity_data["id"] + 5265

            if identity_data["try_number"] == try_ and identity_data["status"] != 0:
                app_context.response["formView"] = True

            app_context.response["reasons"] = identity_data["reasons"]
            if identity_data["document"]:
                uid = get_folder_key(int(identity_data["user_id"]))
                app_context.response["document_url"] = (
                    f"/media/exnr/{uid}/b95f30192536.png?t={int(time.time())}"
                )

        # ---------------- POST ----------------
        if app_context.function.is_post():
            vi_request, error = await get_verify_identity_request(error)

            if not error:
                uid = get_folder_key(int(await app_context.setting.member("id")))
                user_dir = folder.ensure_directory(folder.exnr, uid)
                icon_path = os.path.join(user_dir, "b95f30192536.png")

                if not os.path.exists(icon_path):
                    data = await cls.save_verification_document(
                        vi_request.document_file
                    )
                    if data.get("error"):
                        error["error_document_file"] = data.get("error")
                        return

                ext = os.path.splitext(vi_request.document_file.filename)[1].lower()
                filename = secure_filename("ve_verification" + ext)
                info = json.dumps(app_context.client_info)

                # ---------------- DB ----------------
                db_session = await active_primary_db()
                query = (
                    db_session.query(VerifyIdentity)
                    .filter(VerifyIdentity.user_id == user_id)
                    .first()
                )

                if not query:
                    query = VerifyIdentity(
                        user_id=user_id,
                        document=filename,
                        subject=vi_request.subject,
                        experience=vi_request.experience,
                        document_name=vi_request.document_name,
                        info=info,
                    )
                    db_session.add(query)
                    db_session.commit()
                    db_session.refresh(query)

                await MemberCache.delete_cache(user_id)
                await set_verification_status()
                MetaData.template = "redirect"
                MetaData.redirect_url = "/ut/accounts/teacher/verify-indentity"
                return
        # ---------------- GET FLOW ----------------
        if identity:
            await set_verification_status(identity)
            return "member/teacher_verify_identity"

        return "member/teacher_verify_identity"
