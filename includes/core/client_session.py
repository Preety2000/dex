from datetime import datetime, timedelta

ClientSession = {}

class KS:
    """
    Session-based User client session Cache

    यह class member के session data को memory में store करती है
    ताकि ip के आधार पर member की पहचान (verification) की जा सके।

    हर session में:
    - session_key (member की पहचान के लिए ip)
    - timestamp (session कब बनाया गया)
    शामिल होता है।
    """

    # रोल नंबर के आधार पर session store किया जाता है
    # Format: ip -> (session_key, created_time)
    db: dict[int, tuple[str, datetime]] = ClientSession
    
    EXPIRY_HOURS = 24

    cleanup_time = datetime.now()
    
    @staticmethod
    def _is_expired(created_time: datetime) -> bool:
        """
        Check karta hai ki session expire ho chuka hai ya nahi
        """
        return datetime.now() - created_time > timedelta(hours=KS.EXPIRY_HOURS)

    @staticmethod
    def cleanup():
        """
        Expired sessions ko remove karta hai
        """
        # Update last cleanup time
        KS.cleanup_time = datetime.now()

        # Loop through copy of keys (safe deletion)
        for ip in list(KS.db.keys()):
            _, created_time = KS.db[ip]

            # Agar expired hai to delete kar do
            if KS._is_expired(created_time):
                del KS.db[ip]

    @staticmethod
    def get(ip: int, default: tuple[str, datetime] | None = None) -> tuple[str, datetime] | None:
        """
        किसी भी ip के लिए stored session return करता है।
        अगर session मौजूद नहीं है, तो default value return करता है।
        """
        data = KS.db.get(ip)

        if not data:
            return default

        info, created_time = data
        if KS._is_expired(created_time):
            del KS.db[ip]
            return default

        return info

    @staticmethod
    def add(ip: int, info: str) -> tuple[str, datetime]:
        """
        KS ke basis par session store karta hai with current timestamp

        - Har 1 hour me cleanup trigger hota hai
        """
        now = datetime.now()

        # Periodic cleanup check (1 hour interval)
        if now - KS.cleanup_time > timedelta(hours=1):
            KS.cleanup()

        # Store session
        KS.db[ip] = (info, now)
        return info
    
    @staticmethod
    def remove(ip:str):
        """
        sessions ko remove karta hai
        """
        if KS.db.get(ip):
            del KS.db[ip]
            return