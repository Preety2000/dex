import os
from pathlib import Path
import posixpath
import random
import string
from typing import Optional
from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    Response,
    WebSocket,
)
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    FileResponse,
    StreamingResponse,
)
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from includes.core.repo.upload import extract_uploaded_files
from includes.db_data import SHUTDOWN, STARTUP, download_db_data, import_database
from includes.executers import (
    execute_home_page,
    handle_request_with_cache,
    build_http_response,
    process_account,
)
from includes.core.repo.media import Media
from includes.core.repo.dir_manager import folder
from includes.core.globals.entry import app_context
from includes.core.globals.initialize import initialize_database
from includes.core.metadata import MetaData
from includes.middleware import request_context
from includes.admin.api.api import ADMIN_API
from includes.admin.entry import admin_init
from includes.api.websocket import APIWS
from includes.api.v1.api import API
from includes.qs.qs_index import QS
from includes.schemas.search import Search
from includes.schemas.captcha import Captcha
from includes.schemas.router_schema import DynamicURLRoute
from includes.services.exam.exam import process_exam
from includes.src.string import TextExplorer
from includes.routes.payment import payment_router
from includes.routes.payment import process_payment

app = FastAPI(
    title="Vidya Vistar",
    description="Payment Plan and Pay Now System",
    version="1.0.0",
)

# Mount static folders
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)

template_paths = [
    "templates",
    "static/css",
    "static/script",
    "static/script/cdn",
    "static/script/dm",
    "static/script/sess",
    "static/script/services",
    "static/script/widgets",
]
from jinja2 import ChoiceLoader, FileSystemLoader

templates = Jinja2Templates(directory="templates")
templates.env.loader = ChoiceLoader([FileSystemLoader(path) for path in template_paths])


# Allow CORS for specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(request_context.DataBaseConnectionMiddleware)
app.include_router(payment_router)

# from fastapi_cache.backends.redis import RedisBackend
# # Update your Redis cache initialization
# @app.on_event("startup")
# async def startup():
#     redis_client = redis.from_url("redis://localhost")
#     FastAPICache.entry(RedisBackend(redis_client), prefix="fastapi-cache")


@app.on_event("startup")
async def startup_event():
    await STARTUP()
    print("Application is starting...")


@app.on_event("shutdown")
async def shutdown_event():
    await SHUTDOWN()
    print("Application is shutting down...")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    response = await handle_request_with_cache(callback=execute_home_page)
    response = await build_http_response(response, templates, request)
    response.headers["Cache-Control"] = "public, max-age=3000"
    return response


# Admin Consolidated GET and POST route
@app.api_route(
    "/admin/{root:path}", methods=["GET", "POST"], response_class=HTMLResponse
)
async def admin(root: str | None = None, request: Request = None):
    roots = DynamicURLRoute.parse(root)
    response = await admin_init(roots)
    response = await build_http_response(response, templates, request)
    return response


@app.get("/search", response_class=HTMLResponse)
async def resource(request: Request = None):
    search = Search(request)
    response = await handle_request_with_cache(callback=search.index)
    response = await build_http_response(response, templates, request)
    return response


def generate_captcha_text(length: int = 6) -> str:
    # Confusing characters ko hata diya
    characters = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
    return "".join(random.choice(characters) for _ in range(length))


def generate_cookie_value() -> str:
    return "Ent.5." + "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(40)
    )


@app.get("/img/captcha", response_class=StreamingResponse)
async def captcha(request: Request = None):
    return await Captcha.create()


@app.api_route("/api/{v1}/{root:path}", methods=["GET", "POST"])
async def APIS(request: Request, v1: str = None, root: str | None = None):
    if v1 == "admin":
        apiClass = ADMIN_API(request)
        return await apiClass.index()

    apiClass = API(request)
    return await apiClass.index()


@app.websocket("/ws/{root:path}")
async def websocket_endpoint(websocket: WebSocket, root: str | None = None):
    apiClass = APIWS(websocket)
    await apiClass.index(root)


@app.get("/string/{language}")
@app.get("/string/{language}/{resource}")
async def TExplorer(
    language: str, resource: Optional[str] = None, request: Request = None
):
    textExplorer = TextExplorer()
    response = await textExplorer.get(language, resource)
    return JSONResponse(
        content=response,
        headers={
            "Content-Type": "application/json",
            "Cache-Control": "public, max-age=3000",
        },
    )


@app.get("/script/{filename:path}", response_class=HTMLResponse)
@app.get("/script/{filename:path}", response_class=HTMLResponse)
async def script(filename: str, request: Request):
    if not filename.endswith(".js"):
        filename += ".js"

    file_path = posixpath.join(folder.static_js, filename)

    print(f"Requesting JS file: {filename}, " f"Full path: {file_path}")

    if not os.path.isfile(file_path):
        print(f"JS file NOT FOUND: {file_path}")
        raise HTTPException(
            status_code=404,
            detail=f"JavaScript file not found: {filename}",
        )

    try:

        if "sess" in Path(file_path).parts:
            await initialize_database()
            auth_session = await app_context.setting.member()
            response_object = {
                "request": request,
                "app_context": app_context,
                "function": app_context.function,
                "auth_session": auth_session,
                "svg": app_context.svg_lists,
                **MetaData.to_dict(),
            }

            response = templates.TemplateResponse(
                request=request,
                name=filename,
                context=response_object,
            )

            response.headers["Content-Type"] = "application/javascript"
            return response

        return FileResponse(
            file_path,
            media_type="application/javascript",
        )

    except Exception as e:
        print(f"ERROR while rendering JS {filename}: " f"{type(e).__name__}: {e}")
        raise


@app.api_route("/media/{root:path}", methods=["GET", "POST"])
async def folder_root(root: str | None = None, request: Request = None):
    query = Media(request)
    response = await query.execute()
    if isinstance(response, StreamingResponse) or isinstance(response, Response):
        response.headers["Cache-Control"] = "public, max-age=3000"
        return response

    if isinstance(response, (dict, list)):
        return JSONResponse(content=response, status_code=200)

    return HTMLResponse(
        content=f"{response}", media_type="text/plain; charset=utf-8", status_code=404
    )


# Consolidated GET and POST route
@app.api_route(
    "/ut/accounts/{root:path}", methods=["GET", "POST"], response_class=HTMLResponse
)
async def ut(roots: str = None, request: Request = None):
    response = await process_account(request)
    response = await build_http_response(response, templates, request)
    return response


@app.get("/exam/{root:path}", response_class=HTMLResponse)
async def exam(roots: str = None, request: Request = None):
    response = await handle_request_with_cache(callback=process_exam, allow_catch=None)
    response = await build_http_response(response, templates, request)
    return response


@app.get("/qs/{resource}", response_class=HTMLResponse)
@app.get("/qs/{resource}/{subresource}", response_class=HTMLResponse)
async def exam(
    resource: str, subresource: Optional[str] = None, request: Request = None
):
    return await QS.index(resource, subresource, request, templates)


@app.get("/payment/{root:path}", response_class=HTMLResponse)
async def payment(
    root: str | None = None,
    request: Request = None,
):
    await process_payment()
    auth_session = await app_context.setting.member()
    app_context.response.update(
        {
            "app_context": app_context,
            "function": app_context.function,
            "auth_session": auth_session,
            "device_info": MetaData.device_info,
        }
    )
    response = await build_http_response(app_context.response, templates, request)
    return response


@app.post("/stro/upload/{root:path}")
async def upload_json(root: str = None):

    form = await app_context.request.form()
    file = await extract_uploaded_files("file")

    print("Uploaded file:", file)

    if file is None:
        raise HTTPException(status_code=400, detail="JSON file is required")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing")

    if not file.filename.lower().endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON files are allowed")

    try:
        content = await file.read()

        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        import json

        result = json.loads(content)
        stats = await import_database(root, result)

        return {"success": True, "message": "JSON imported successfully", **stats}

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON file: {e}")

    except HTTPException:
        raise

    except Exception as e:
        import traceback

        traceback.print_exc()

        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@app.get("/stro/{root:path}")
async def download_data(root: str | None = None, request: Request = None):
    return await download_db_data(root, templates, request)


@app.api_route("/{roots:path}", methods=["GET"], response_class=HTMLResponse)
async def resource(request: Request, roots: str):
    roots = DynamicURLRoute.parse(roots)

    response = await handle_request_with_cache()
    response = await build_http_response(response, templates, request)

    return response


# ngrok http 8000

# python -m uvicorn main:app --reload
# python -m uvicorn main:app --reload --ssl-keyfile key.pem --ssl-certfile cert.pem
# python -m uvicorn main:app --workers 4 --ssl-keyfile key.pem --ssl-certfile cert.pem


# pip freeze > requirements.txt
