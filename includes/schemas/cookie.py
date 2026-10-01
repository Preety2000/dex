from urllib.parse import urlparse
from fastapi import Request

class Cookie():
    def __init__(self, request:Request):
        self.request = request
        
    def start(self):
        self.set_item = {}

    @staticmethod
    def get_domain(request):
        parsed_url = urlparse(str(request.url))
        domain = parsed_url.hostname

        # Remove subdomains if present
        for subdomain in ["www.", "history."]:
            if domain.startswith(subdomain):
                domain = domain[len(subdomain):]

        return domain

    def get(self, cookie_name):
        return self.request.cookies.get(cookie_name, None)

    def insert(self, name, value, max_age=None):
        self.set_item[name] = {
            "value": value,
            "max_age": max_age
        }

    def update(self, cookie_name, cookie_value, max_age=None):
        self.insert(cookie_name, cookie_value, max_age)

    def domain(self, name, value, max_age=None):
        domain = self.get_domain(self.request)
        max_age = max_age * 60*60*24 if isinstance(max_age, (int, float)) else max_age

        self.set_item[name] = {
            "value": value,
            "domain": domain,
            "max_age": max_age
        }

    def delete(self, cookie_name):
        self.set_item[cookie_name] = {
            "value": None,
            "max_age": 0
        }
    
    async def setcookie(self, headers):

        for name, cookie in self.set_item.items():
            parts = []
            # cookie key=value
            key = name.encode()
            value = cookie.get("value", "")
            cookie_str = f"{name}={value}"

            parts.append(cookie_str)

            # Add optional cookie attributes
            max_age = cookie.get("max_age")
            if max_age is not None:
                parts.append(f"Max-Age={max_age}")

            domain = cookie.get("domain")
            if domain:
                parts.append(f"Domain={domain}")

            path = cookie.get("path", "/")
            if path:
                parts.append(f"Path={path}")

            # if cookie.get("httponly", True):
            #     parts.append("HttpOnly")

            if cookie.get("secure", False):
                parts.append("Secure")

            samesite = cookie.get("samesite")
            if samesite:
                parts.append(f"SameSite={samesite}")

            # Join all parts separated by semicolon and space
            header_value = "; ".join(parts)

            # Append header as bytes
            headers.append((
                b"set-cookie",
                header_value.encode()
            ))
    