from typing import Any
from datetime import datetime, timedelta

Cache = {}
Event = {}

class AppCache:
    """
    Application Level Memory Cache
    Cache Format:
        key -> (value, created_at)

    विशेषताएँ:
    - Data memory में store होता है।
    - Cache 24 घंटे तक valid रहता है।
    - 24 घंटे से पुराना data अपने आप हट जाता है।
    """

    TTL = timedelta(hours=24)
    ev: dict[str, callable] = Event
    db: dict[Any, tuple[Any, datetime]] = Cache

    @classmethod
    def get(cls, key: Any, default: Any = None) -> Any:
        """
        Cache से data प्राप्त करें।

        यदि:
        - key मौजूद नहीं है → default return होगा
        - data 24 घंटे से पुराना है → cache से हटाकर default return होगा
        - data valid है → value return होगी
        """

        item = cls.db.get(key)
        if item is None:
            return default

        value, created_at = item
        if datetime.now() - created_at > cls.TTL:

            del cls.db[key]
            return default

        return value

    @classmethod
    def add(cls, key: Any, value: Any, timing: datetime = None) -> tuple[Any, datetime]:
        """
        Cache में नया data store करें।
        Return: value
        """

        created_at = datetime.now()
        # cls.db[key] = (value, created_at)

        return value

    @classmethod
    def delete(cls, key: Any) -> bool:
        """
        Cache से किसी key को हटाएँ।
        Return:
            True  -> हट गई
            False -> key मौजूद नहीं थी
        """

        if key in cls.db:
            del cls.db[key]
            return True

        return False

    @classmethod
    def exists(cls, key: Any) -> bool:
        """
        Check करें कि key cache में मौजूद है या नहीं।
        """

        # पहले ही साफ हो जाए
        return cls.get(key) is not None

    @classmethod
    def created_at(cls, key: Any) -> datetime | None:
        """
        Cache entry का creation time प्राप्त करें।
        यदि key नहीं मिली या expire हो गई है
        तो None return होगा।
        """

        item = cls.db.get(key)

        if item is None:
            return None

        _, created_at = item

        # Expiry check
        if datetime.now() - created_at > cls.TTL:
            del cls.db[key]
            return None

        return created_at

    @classmethod
    def clear(cls) -> None:
        """पूरा cache साफ करें।"""
        cls.db.clear()

    @classmethod
    def size(cls) -> int:
        """वर्तमान में cache में कितनी entries हैं।"""

        return len(cls.db)

    @classmethod
    def cleanup(cls) -> int:
        """सभी expired entries हटाएँ।
        Return: हटाई गई entries की संख्या
        """

        now = datetime.now()

        expired_keys = [
            key for key, (_, created_at) in cls.db.items() if now - created_at > cls.TTL
        ]

        for key in expired_keys:
            del cls.db[key]

        return len(expired_keys)
