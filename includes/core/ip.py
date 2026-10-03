import hashlib
import requests

from datetime import datetime, timedelta
from includes.core.client_info import collect_user_signals
from includes.core.deviceinfo import DeviceInfo
from includes.core.globals.entry import app_context
from includes.core.metadata import MetaData


def generate_fingerprint(request):
    headers = {
        "ua": request.headers.get("User-Agent", ""),
        "lang": request.headers.get("Accept-Language", ""),
        "enc": request.headers.get("Accept-Encoding", ""),
        "plat": request.headers.get("Sec-CH-UA-Platform", ""),
        "mobile": request.headers.get("Sec-CH-UA-Mobile", ""),
    }

    ip = request.headers.get("X-Forwarded-For", request.ip)
    raw = "|".join([ip, *headers.values()])

    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


TempIp = {}


class IP:
    """
    IP-based Session Store
    - Har IP ke saath session info store hota hai
    - Auto expiry: 24 hours
    - Periodic cleanup: every 1 hour
    """

    # IP -> (session_info, created_time)
    db: dict[str, tuple[str, datetime]] = TempIp

    # Session expiry time limit
    EXPIRY_HOURS = 24

    # Last cleanup timestamp (class-level state)
    cleanup_time = datetime.now()

    @staticmethod
    def _is_expired(created_time: datetime) -> bool:
        """
        Check karta hai ki session expire ho chuka hai ya nahi
        """
        return datetime.now() - created_time > timedelta(hours=IP.EXPIRY_HOURS)

    @staticmethod
    def get(ip: str, default=None):
        """
        IP ke basis par session data return karta hai

        - Agar IP exist nahi karta → default return
        - Agar session expire ho gaya → delete karke default return
        """
        data = IP.db.get(ip)

        if not data:
            return default

        info, created_time = data

        # Expiry check
        if IP._is_expired(created_time):
            del IP.db[ip]  # expired session remove
            return default

        return info

    @staticmethod
    def add(ip: str, info: str):
        """
        IP ke basis par session store karta hai with current timestamp

        - Har 1 hour me cleanup trigger hota hai
        """
        now = datetime.now()

        # Periodic cleanup check (1 hour interval)
        if now - IP.cleanup_time > timedelta(hours=1):
            IP.cleanup()

        # Store session
        IP.db[ip] = (info, now)
        return info

    @staticmethod
    def cleanup():
        """
        Expired sessions ko remove karta hai
        """
        # Update last cleanup time
        IP.cleanup_time = datetime.now()

        # Loop through copy of keys (safe deletion)
        for ip in list(IP.db.keys()):
            _, created_time = IP.db[ip]

            # Agar expired hai to delete kar do
            if IP._is_expired(created_time):
                del IP.db[ip]

    @staticmethod
    def get_info() -> dict:
        """
        IP information fetch karta hai.

        Flow:
        1. Pehle local cache check karta hai
        2. Agar cache miss ho to external API (ipinfo.io) call karta hai
        3. Successful response ko cache me store karta hai
        4. Failure par None return karta hai
        """

        fingerprint_id = generate_fingerprint(app_context.request)
        cached_data = IP.get(fingerprint_id)

        if cached_data:
            cached_data["device"] = DeviceInfo.to_dict()
            MetaData.client_info = cached_data
            app_context.client_info = cached_data
            return cached_data

        try:
            info = collect_user_signals(app_context.request.ip)
            client_info = IP.add(fingerprint_id, info)
            MetaData.client_info = client_info
            app_context.client_info = cached_data
            return client_info

        except requests.RequestException as e:
            # Optional: logging can be added here
            # print(f"[IPINFO ERROR] {e}")
            app_context.client_info = {}
            return {}
