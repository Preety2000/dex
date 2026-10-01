import aiofiles
from fastapi.responses import HTMLResponse, Response

from includes.core.globals.coreutils import process_image
from includes.schemas.sitemap import Sitemap


class StaticRouteHandler:
    """Special/Static routes (favicon, sitemap, robots.txt) handle karne ke liye alag module"""

    @staticmethod
    async def handle_static_route(scope_type: str):
        if scope_type == "favicon.ico":
            return process_image("favicon.png", "ico")

        if scope_type == "sitemap.xml":
            xml_data = Sitemap.sitemap()
            return HTMLResponse(content=xml_data, media_type="application/xml")

        if scope_type == "opensearch.xml":
            xml_data = Sitemap.opensearch()
            return HTMLResponse(content=xml_data, media_type="application/xml")

        if scope_type == "robots.txt":
            # Non-blocking async file reading
            async with aiofiles.open("robots.txt", mode="r") as file:
                file_content = await file.read()

            return Response(
                content=file_content,
                media_type="text/plain",
                status_code=200,
                headers={"Cache-Control": "no-cache, no-store, max-age=0, must-revalidate"},
            )

        return None


