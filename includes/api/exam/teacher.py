from dataclasses import fields

from sqlalchemy import desc
from includes.api.exam.metadata import (
    AccessRestricted,
    build_settings_page,
    s_meta_value,
)
from includes.core.globals.entry import app_context
from includes.db.connection import active_exam_db
from includes.db.models.db_exam import _TeacherProfile, TeacherProfile
from includes.utils.utils import get_post_value, json_response


async def create_teacher_profile(insurt_data: _TeacherProfile, option: bool = None):

    db = await active_exam_db()
    query = db.query(TeacherProfile).filter(TeacherProfile.id == insurt_data.id).first()

    if option is True:
        if query is None:
            return json_response({"jump": "/exam/r/setting?qc=account"})

        query.join_mode = insurt_data.join_mode
        query.open_request = insurt_data.open_request
        query.exam_category = insurt_data.exam_category
        query.req_appr_mode = insurt_data.req_appr_mode
        query.result_visibility = insurt_data.result_visibility
        db.commit()

        return json_response(
            {
                "__ac": 405,
                "title": "Welcome, Educator!",
                "content": [
                    "Thank you for joining our teaching community.",
                    "We look forward to empowering you every step of the way.",
                    {
                        "tagName": "a",
                        "inner": "👉 Go Teaching Dashboard!",
                        "href": "/exam/r/dashboard",
                    },
                ],
            }
        )

    if query is None:
        query = TeacherProfile(
            id=insurt_data.id,
            img=insurt_data.img,
            name=insurt_data.name,
            biography=insurt_data.biography,
            signature=insurt_data.signature,
        )
        db.add(query)
    else:
        query.img = insurt_data.img
        query.name = insurt_data.name
        query.biography = insurt_data.biography
        query.signature = insurt_data.signature

    db.commit()

    return json_response({"jump": "/exam/r/setting?qc=behaviors&required=true"})


async def check_teacher_authorization(verification_status):
    """
    Validate member educational authorization and teacher setup status.
    Returns: (verification_status, response_payload)
    """
    if not verification_status:
        return None

    user_id = await app_context.setting.member("id")
    language = await app_context.setting.get("language", "English")

    # 1. Check educational authorization
    edu_auth = await app_context.setting.member("eduAuth", False)

    if not edu_auth:
        return json_response(AccessRestricted.get(language, "Access Restricted"))

    # 2. Get teacher profile
    teacher_meta = await Teachers.get(user_id)

    # 3. Teacher profile does not exist
    if teacher_meta is None:
        update = {
            name: await get_post_value(name)
            for name in ["biography", "img", "signature", "name"]
        }

        # All required fields are present
        if all(value and str(value).strip() for value in update.values()):
            teacher_profile = _TeacherProfile(
                id=user_id,
                **update,
            )

            return await create_teacher_profile(teacher_profile)

        # Some fields are present, but not all
        if any(value and str(value).strip() for value in update.values()):
            return json_response(
                {"message": ("Please select a value that meets the requirements. *")}
            )

        # Nothing submitted yet
        return json_response(await build_settings_page(language))
    # 4. Teacher profile exists but join_mode is not configured
    if teacher_meta.join_mode is None:

        referer = app_context.request.referer.params

        if referer.get("qc") != "behaviors" or referer.get("required") != "true":
            return json_response({"jump": "/exam/r/setting?qc=behaviors&required=true"})

        update = {"exam_category": await get_post_value("exam_category")}

        # Map submitted values to their index
        for name in ["join_mode", "open_request", "req_appr_mode", "result_visibility"]:
            values = s_meta_value.get(name, [])
            value = await get_post_value(name)

            update[name] = values.index(value) if value in values else None

        # Everything required is valid
        if all(value is not None for value in update.values()):
            for field in fields(teacher_meta):
                if field.name in update:
                    setattr(
                        teacher_meta,
                        field.name,
                        update[field.name],
                    )

            return await create_teacher_profile(
                teacher_meta,
                True,
            )

        # At least one field was submitted
        if any(value is not None for value in update.values()):
            return json_response(
                {"message": ("Please select a value that meets the requirements. *")}
            )

        # Nothing submitted
        return json_response(await build_settings_page(language))

    # 5. Everything is already configured
    return teacher_meta


TeachersMetaTamp = {}


class Teachers:

    @staticmethod
    async def with_catch(record: TeacherProfile) -> _TeacherProfile:
        TeachersMetaTamp[record.id] = record.to_dataclass()
        return TeachersMetaTamp[record.id]

    @staticmethod
    async def get(id: int):
        if id in TeachersMetaTamp:
            return TeachersMetaTamp[id]

        query = (
            app_context.db.query(TeacherProfile).filter(TeacherProfile.id == id).first()
        )
        return await Teachers.with_catch(query) if query else None

    @staticmethod
    async def update(session: _TeacherProfile):
        record = (
            app_context.db.query(TeacherProfile)
            .filter(TeacherProfile.id == session.id)
            .first()
        )

        record.name = session.name
        record.img = session.img
        record.biography = session.biography
        record.signature = session.signature
        record.join_mode = session.join_mode
        record.open_request = session.open_request
        record.req_appr_mode = session.req_appr_mode
        record.result_visibility = session.result_visibility
        record.exam_category = session.exam_category

        app_context.db.commit()
        app_context.db.refresh(record)
        return await Teachers.with_catch(record)
