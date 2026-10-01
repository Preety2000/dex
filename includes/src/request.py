from ast import Dict
from typing import Optional
import uuid

import requests
from fastapi import Request
from urllib.parse import parse_qs, urlparse

from dataclasses import dataclass, field


@dataclass
class RequestContext:
    path: str
    query: str
    params: str
    base_url: str
    base_uri: str
    full_path: str
    url_root: str
    host_url: str
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # semantic URL segments
    resource: Optional[str] = None
    subresource: Optional[str] = None
    action: Optional[str] = None
    section: Optional[str] = None
    item: Optional[str] = None

    # extra: store remaining path segments dynamically
    extra_segments: dict[str, str] = field(default_factory=dict)

def components(url: str = None)-> RequestContext:
    parsed = urlparse(str(url or ""))
    scheme = parsed.scheme or "http"
    netloc = parsed.netloc
    path = parsed.path
    query = parsed.query
    
    # Parse query parameters
    raw_params = parse_qs(query)
    params = {k: v[0] if len(v) == 1 else v for k, v in raw_params.items()}
    url_root = f"{scheme}://{netloc}"
    base_url = f"{url_root}{path}"
    full_path = f"{base_url}?{query}" if query else base_url
            
    segments = [s for s in parsed.path.strip("/").split("/") if s]
    
    # assign semantic names
    resource = segments[0] if len(segments) > 0 else None
    subresource = segments[1] if len(segments) > 1 else None
    action = segments[2] if len(segments) > 2 else None
    section = segments[3] if len(segments) > 3 else None
    item = segments[4] if len(segments) > 4 else None
    
    # remaining segments beyond 5
    extra_segments = {f"extra_{i+6}": seg for i, seg in enumerate(segments[5:])}
    return RequestContext(
        path=path,
        query=query,
        params=params,
        base_url=base_url,
        base_uri=base_url,
        full_path=full_path,
        url_root=url_root,
        host_url=f"{url_root}/",
        request_id=str(uuid.uuid4()),
        
        resource=resource,
        subresource=subresource,
        action=action,
        section=section,
        item=item,
        extra_segments=extra_segments
    )
    
def Requests(request: Request):
    component = components(str(request.url))
    
    request.path = component.path
    request.query = component.query
    request.params = component.params
    request.url_root = component.url_root
    request.host_url = component.host_url
    request.base_uri = component.base_url
    request.full_path = component.full_path
    
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    request.ip = (
        x_forwarded_for.split(",")[0].strip()
        if x_forwarded_for
        else (request.client.host if request.client else "0.0.0.0")
    )
    
    # Parse and store referer URL component if available
    referer_url = request.headers.get("Referer")
    request.referer = (
        components(referer_url) 
        if referer_url else None
    )
    
    return request
        

class requestComponents:
    def __init__(self, request: Request):
        components = components(str(request.url))

        request.path = components.path
        request.query = components.query
        request.params = components.params
        request.url_root = components.url_root
        request.host_url = components.host_url
        request.base_uri = components.base_url
        request.full_path = components.full_path

        # Get client IP, prioritizing X-Forwarded-For header
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        request.ip = (
            x_forwarded_for.split(",")[0].strip()
            if x_forwarded_for
            else (request.client.host if request.client else "0.0.0.0")
        )

        # Parse and store referer URL components if available
        self.ip = request.ip
        referer_url = request.headers.get("Referer")
        request.referer = self.components(referer_url) if referer_url else None
        request.ipinfo = self.ipinfo
        request.components = self.components

    def components(self, url: str = None)-> RequestContext:
        parsed = urlparse(str(url or ""))

        scheme = parsed.scheme or "http"
        netloc = parsed.netloc
        path = parsed.path
        query = parsed.query

        # Parse query parameters
        raw_params = parse_qs(query)
        params = {k: v[0] if len(v) == 1 else v for k, v in raw_params.items()}

        url_root = f"{scheme}://{netloc}"
        base_url = f"{url_root}{path}"
        full_path = f"{base_url}?{query}" if query else base_url
                
        segments = [s for s in parsed.path.strip("/").split("/") if s]

        # assign semantic names
        resource = segments[0] if len(segments) > 0 else None
        subresource = segments[1] if len(segments) > 1 else None
        action = segments[2] if len(segments) > 2 else None
        section = segments[3] if len(segments) > 3 else None
        item = segments[4] if len(segments) > 4 else None

        # remaining segments beyond 5
        extra_segments = {f"extra_{i+6}": seg for i, seg in enumerate(segments[5:])}

        return RequestContext(
            path=path,
            query=query,
            params=params,
            base_url=base_url,
            full_path=full_path,
            url_root=url_root,
            host_url=f"{url_root}/",
            request_id=str(uuid.uuid4()),
            
            resource=resource,
            subresource=subresource,
            action=action,
            section=section,
            item=item,
            extra_segments=extra_segments
        )

    def ipinfo(self, data=None):
        data = data or {}
        ipinfo_url = f"https://ipinfo.io/{self.ip}/json"
        try:
            response = requests.get(ipinfo_url, timeout=3)
            if response.status_code == 200:
                data = response.json()
        except requests.RequestException:
            pass
        return data

    def __iter__(self):
        return iter(vars(self).items())

    @property
    def json(self):
        return {key: value for key, value in vars(self).items()}
