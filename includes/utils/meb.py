import os
import re
import copy
from datetime import datetime
from typing import Any,  List, Optional

from sqlalchemy import select
from includes.core.device_encoder import decode_device
from includes.core.repo.dir_manager import folder
from includes.database.models.utils import TimeStamp
from includes.core.security import _Security
from includes.database.models.owner import MemberSession

GENDER = ["Prefer not to say", "Female", "Male"]


def extract_id_from_roll(roll_no: str):
    roll_no = str(roll_no)

    if len(roll_no) >= 2 and roll_no[:2].isdigit():
        roll_no = roll_no[2:]

    if len(roll_no) == 8:
        return int(roll_no[2:])

    return None


def generate_roll_and_reg(record):
    cunt_year = str(datetime.now().year)[-2:]
    roll_no = int(cunt_year + str(record["id"]).zfill(8))
    reg_no = f"NS/{str(record["reg_no"]).zfill(5)}/{cunt_year}"

    return roll_no, reg_no


async def format_session_info(
    record: MemberSession, session_ids: Optional[List[int]] = None
) -> dict[str, Any]:
    session_ids = session_ids or []
    return {
        "active": record.id in session_ids,
        "isActive": record.is_active,
        "loginTime": TimeStamp.format_ts(record.login_time, "%d %B, %Y at %I:%M %p"),
        "logoutTime": TimeStamp.format_ts(record.logout_time, "%d %B, %Y at %I:%M %p"),
        "ipInformation": record.ip_address,
        "deviceInformation": decode_device(record.device_id),
    }


def serialize_member(record: dict) -> dict:
    if not isinstance(record, dict):
        return record

    _record = copy.deepcopy(record)

    if not _record.get("password"):
        return _record

    image_src = _record.get("image_src", _Security.short_encode("image.png"))
    _record["roll_no"], _record["reg_no"] = generate_roll_and_reg(_record)

    if _record["identity"]:
        _record["eduAuth"] = _record["identity"]["status"] == 1

    _record["gender"] = GENDER[int(_record.get("gender", 0) or 0)]
    _record["role"] = [None, "Student", "Teacher", "Blocked"][_record["status"]]
    _record["img"] = (
        f"/media/u/{get_email_folder_info(_record["id"])}/{image_src or 'image.png'}"
    )

    del _record["password"]

    return _record


def resolve_image_name(encode_number: str):

    if re.search(r"\d+", str(encode_number)):
        encode_number = _Security.short_encode(encode_number)

    return encode_number


def get_email_folder_info(identifier: str, return_encoded: bool = None):
    if identifier is None:
        raise ValueError("Phone cannot be None")

    identifier = str(identifier).strip()
    encode_number = resolve_image_name(identifier)

    if return_encoded is None:
        return encode_number

    folder_root = os.path.join(folder.member_folder, encode_number)

    if return_encoded is False:
        try:
            number = _Security.short_decode(encode_number)
        except:
            number = None

        return number, folder_root

    return encode_number, folder_root


# def resolve_image_name(identifier: str):
#     prefix = "utl_"

#     if "@" in identifier:
#         email_name = identifier.split("@", 1)[0]
#         return email_name, prefix + _Security.short_encode(email_name)

#     encoded_name = identifier[len(prefix):] if identifier.startswith(prefix) else identifier
#     return _Security.short_decode(encoded_name), identifier

# def get_email_folder_info(identifier: str, return_encoded: bool = None):
#     if identifier is None:
#         raise ValueError("email cannot be None")

#     identifier = str(identifier).strip()
#     try: email_name, encoded_name = resolve_image_name(identifier)
#     except: email_name, encoded_name = "user", "MjE1Mjg5NzQ0"

#     if return_encoded is None:
#         return encoded_name

#     folder_root = folder.ensure_directory(folder.member_folder, email_name)
#     os.makedirs(folder_root, exist_ok=True)

#     if return_encoded is False:
#         return email_name, folder_root

#     return encoded_name, folder_root
