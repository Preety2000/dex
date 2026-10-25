import aiofiles
from includes.src.request import Request
from fastapi.responses import HTMLResponse, Response

from includes.core.globals.coreutils import process_image
from includes.schemas.sitemap import Sitemap


class StaticRouteHandler:
    """Special/Static routes (favicon, sitemap, robots.txt) handle karne ke liye alag module"""

    @staticmethod
    async def handle_static_route(request: Request = None, file_path: str = None):
        if file_path == "favicon.ico":
            return await process_image("favicon.png", "ico")

        if file_path == "sitemap.xml":
            xml_data = Sitemap.sitemap()
            return HTMLResponse(content=xml_data, media_type="application/xml")

        if file_path == "opensearch.xml":
            xml_data = Sitemap.opensearch(request)
            return HTMLResponse(content=xml_data, media_type="application/xml")

        if file_path == "robots.txt":
            # Non-blocking async file reading
            async with aiofiles.open("robots.txt", mode="r") as file:
                file_content = await file.read()

            return Response(
                content=file_content,
                media_type="text/plain",
                status_code=200,
                headers={
                    "Cache-Control": "no-cache, no-store, max-age=0, must-revalidate"
                },
            )

        return None
