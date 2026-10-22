from uuid import uuid4
from fastapi import Request, WebSocket
from urllib.parse import urlparse, parse_qs


def get_ip(self):
    return self.client.host if self.client else None


def get_path(self):
    return urlparse(str(self.url)).path


def get_query(self):
    return urlparse(str(self.url)).query


def get_params(self):
    query = self.query
    raw = parse_qs(query)
    return {k: v[0] if len(v) == 1 else v for k, v in raw.items()}


def get_url_root(self):
    parsed = urlparse(str(self.url))
    scheme = parsed.scheme or "http"
    return f"{scheme}://{parsed.netloc}"


def get_base_url(self):
    return f"{self.url_root}{self.path}"


def get_base_uri(self):
    return self.base_url


def get_full_path(self):
    return f"{self.base_url}?{self.query}" if self.query else self.base_url


def get_host_url(self):
    return f"{self.url_root}/"


def get_request_id(self):
    if not hasattr(self.state, "_request_id"):
        self.state._request_id = str(uuid4())
    return self.state._request_id


def get_referer(self):
    url = self.headers.get("Referer")
    if url is None:
        return None

    from includes.src.referer import Referer

    return Referer(self)


def is_post(self):
    return self.method == "POST"


# Register properties globally
Request.ip = property(get_ip)
Request.path = property(get_path)
Request.query = property(get_query)
Request.params = property(get_params)
Request.url_root = property(get_url_root)
Request.base_url = property(get_base_url)
Request.base_uri = property(get_base_uri)
Request.full_path = property(get_full_path)
Request.host_url = property(get_host_url)
Request.request_id = property(get_request_id)
Request.referer = property(get_referer)
Request.is_post = property(is_post)

# Register properties globally
WebSocket.ip = property(get_ip)
WebSocket.path = property(get_path)
WebSocket.query = property(get_query)
WebSocket.params = property(get_params)
WebSocket.url_root = property(get_url_root)
WebSocket.base_url = property(get_base_url)
WebSocket.base_uri = property(get_base_uri)
WebSocket.full_path = property(get_full_path)
WebSocket.host_url = property(get_host_url)
WebSocket.request_id = property(get_request_id)
WebSocket.referer = property(get_referer)
WebSocket.is_post = property(is_post)


# import uuid
# from typing import Optional
# from urllib.parse import parse_qs, urlparse
# from dataclasses import dataclass, field

# from includes.src.request import Request
# from includes.src.referer import Referer
# from includes.core.globals.route_context import Route


# Request.ip = property(lambda self: self.client.host if self.client else None)


# @dataclass
# class RequestContext:
#     path: str = ""
#     query: str = ""
#     params: dict = field(default_factory=dict)

#     base_url: str = ""
#     base_uri: str = ""
#     full_path: str = ""
#     url_root: str = ""
#     host_url: str = ""

#     request_id: str = field(default_factory=lambda: str(uuid.uuid4()))

#     # Semantic URL segments
#     depth: int = 0
#     raw_path: str = ""

#     # Referer object
#     referer: Optional["Referer"] = None

#     # Fixed level parameters
#     section: Optional[str] = None
#     scope: Optional[str] = None
#     entity: Optional[str] = None
#     action: Optional[str] = None
#     core: Optional[str] = None
#     space: Optional[str] = None
#     end: Optional[str] = None

#     def __init__(self, request):
#         parsed = urlparse(str(request.url))

#         scheme = parsed.scheme or "http"
#         netloc = parsed.netloc

#         self.path = parsed.path
#         self.query = parsed.query

#         raw_params = parse_qs(self.query)
#         self.params = {
#             key: values[0] if len(values) == 1 else values
#             for key, values in raw_params.items()
#         }

#         self.url_root = f"{scheme}://{netloc}"
#         self.base_url = f"{self.url_root}{self.path}"
#         self.base_uri = self.base_url
#         self.full_path = (
#             f"{self.base_url}?{self.query}"
#             if self.query else self.base_url
#         )
#         self.host_url = f"{self.url_root}/"
#         self.request_id = str(uuid.uuid4())

#         # Route information
#         route = Route(parsed.path)
#         self.depth = route.depth
#         self.raw_path = route.raw_path

#         self.section = route.section
#         self.scope = route.scope
#         self.entity = route.entity
#         self.action = route.action
#         self.core = route.core
#         self.space = route.space
#         self.end = route.end

#         # Referer header
#         referer_url = request.headers.get("Referer")
#         self.referer = (
#             Referer(referer_url)
#             if referer_url is not None
#             else None
#         )

#         # IP
#         client = getattr(request, "client", None)
#         self.ip = getattr(client, "host", None)
