import gzip
import brotli

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class CompressionMiddleware(BaseHTTPMiddleware):

    MINIMUM_SIZE = 1000
    BROTLI_QUALITY = 5
    GZIP_LEVEL = 6

    COMPRESSIBLE_TYPES = (
        "text/",
        "application/json",
        "application/javascript",
        "application/xml",
        "application/xhtml+xml",
        "image/svg+xml",
    )

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # No body
        if request.method == "HEAD" or response.status_code in (204, 304):
            return response

        # Already encoded
        if response.headers.get("content-encoding"):
            return response

        content_type = response.headers.get("content-type", "").lower()

        # Non-compressible content
        if not content_type.startswith(self.COMPRESSIBLE_TYPES):
            return response

        body = b"".join(
            [chunk async for chunk in response.body_iterator]
        )

        # Original Content-Length ko kabhi reuse mat karo
        headers = dict(response.headers)
        headers.pop("content-length", None)

        # Small response
        if len(body) < self.MINIMUM_SIZE:
            headers["content-length"] = str(len(body))

            return Response(
                content=body,
                status_code=response.status_code,
                headers=headers,
                media_type=None,
            )

        accept_encoding = request.headers.get(
            "accept-encoding",
            "",
        ).lower()

        encoding = None

        if "br" in accept_encoding:
            body = brotli.compress(
                body,
                quality=self.BROTLI_QUALITY,
            )
            encoding = "br"

        elif "gzip" in accept_encoding:
            body = gzip.compress(
                body,
                compresslevel=self.GZIP_LEVEL,
            )
            encoding = "gzip"

        # No supported compression
        if encoding is None:
            headers["content-length"] = str(len(body))

            return Response(
                content=body,
                status_code=response.status_code,
                headers=headers,
                media_type=None,
            )

        headers["content-encoding"] = encoding
        headers["content-length"] = str(len(body))

        vary = headers.get("vary")

        if vary:
            if "accept-encoding" not in vary.lower():
                headers["vary"] = f"{vary}, Accept-Encoding"
        else:
            headers["vary"] = "Accept-Encoding"

        return Response(
            content=body,
            status_code=response.status_code,
            headers=headers,
            media_type=None,
        )
