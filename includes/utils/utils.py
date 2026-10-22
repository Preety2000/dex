import re
import unicodedata
from typing import Any, Callable
from datetime import datetime, timezone
from sqlalchemy import text

from includes.src.request import Request


def set_response(request, name, value):
    request.state.response[name] = value
    return request.state.response


def redirect_back(request, default: str = "/"):
    request.state.metadata.template = "redirect"
    request.state.metadata.redirect_url = (
        request.state.referer.full_path
        if request.path != request.state.referer.path
        else default
    )


def get_referer(request: Request = None):
    try:
        return request.state.referer
    except AttributeError:
        return None


def get_referer_value(request, value, default=None):

    referer = get_referer(request)
    if referer is None:
        return None

    params = getattr(referer, "params", {})
    return params.get(value, default)


def get_query_num(query_params, key, default=None):
    value = query_params.get(key)
    try:
        num = float(value)
        return int(num) if num.is_integer() else num
    except (TypeError, ValueError):
        return default


async def get_post_value(request: Request, name, value=None):
    try:
        form = await request.json()
    except:
        try:
            form = await request.form()
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


def _resolve_request_getter( request: Request, source: str | None = None, key: str | None = None) -> Callable | Any:
    if source in (None, "query"):
        getter = request.query_params.get

    elif source == "api":
        getter = lambda k: get_post_value(request, k)

    elif source == "referer":
        getter = lambda k: get_referer_value(request, k)

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
