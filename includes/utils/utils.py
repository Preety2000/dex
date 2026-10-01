import re
import unicodedata
from typing import Any, Callable
from datetime import datetime, timezone

from sqlalchemy import MetaData, text
from includes.core.globals.entry import app_context


def set_response(name, value):
    app_context.response[name] = value
    return app_context.response


def redirect_back(default: str = "/"):
    MetaData.template = "redirect"
    MetaData.redirect_url = (
        app_context.request.referer.full_path
        if app_context.request.path != app_context.request.referer.path
        else default
    )


def get_referer():
    try:
        return app_context.request.referer
    except AttributeError:
        return None


def get_referer_value(value, default=None):

    referer = get_referer()
    if referer is None:
        return None

    params = getattr(referer, "params", {})
    return params.get(value, default)


def get_query_value(value, default=None):
    return app_context.request.query_params.get(value, default)


async def get_post_value(name, value=None):
    try:
        form = await app_context.request.json()
    except:
        try:
            form = await app_context.request.form()
        except:
            form = {}
    if isinstance(form, list):
        return form if name is True else value

    if isinstance(name, bool):
        return value

    if isinstance(name, list):
        out = {}
        for i, n in enumerate(name):
            v = form.get(n)
            if re.search(r"\[\]", n):
                v = form.getlist(n)
                n = n.replace("[]", "")
            if not v:
                v = value[i] if isinstance(value, list) else value
            out[n] = v
        return out

    return (
        form.getlist(name)
        if re.search(r"\[\]", name)
        else form.get(name, value) or value
    )


def _resolve_request_getter(
    source: str | None = None, key: str | None = None
) -> Callable | Any:
    if source in (None, "query"):
        getter = get_query_value

    elif source == "api":
        getter = get_post_value

    elif source == "referer":
        getter = get_referer_value

    else:
        raise ValueError(
            f"Invalid source: {source!r}. " "Expected: 'query', 'api', or 'referer'."
        )

    if key is None:
        return getter

    return getter(key)


def create_slug(text):
    # Normalize the text to remove accents and special characters
    text = unicodedata.normalize("NFKD", text)
    # Convert to lowercase
    text = text.lower()
    # Remove special characters using regex
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    # Replace spaces and consecutive hyphens with a single hyphen
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text


def get_next_id(db, table):
    t = table.__tablename__
    return db.execute(text(f"""
        SELECT CASE
            WHEN NOT EXISTS (SELECT 1 FROM {t} WHERE id = 1) THEN 1
            ELSE (
                SELECT MIN(a.id + 1)
                FROM {t} a
                LEFT JOIN {t} b ON b.id = a.id + 1
                WHERE b.id IS NULL
            )
        END
    """)).scalar()


def json_null_response(*, code: str = None, details: Any = None):
    return json_response(
        error={
            "code": code,
            "details": details,
        }
    )


def json_response(
    data: Any = None,
    *,
    message: str | None = None,
    error: Any = None,
    request_id: str | None = None,
    success: bool = True,
):

    responce1 = [success]

    responce = {
        "status": "ok" if success else "error",
        "trace": {
            "id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }

    if error is not None:
        responce["error"] = error
    if message is not None:
        responce["message"] = message

    responce1.append(responce)
    if data is not None:
        responce1.append(data)

    return responce1

    return [{"status": "ok", "RESTFUL": query}, None]



