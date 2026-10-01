from datetime import datetime

AuthSessionStore = {}

class ES:
    """
    Session-based User Verification Cache

    यह class member के session data को memory में store करती है
    ताकि roll number के आधार पर member की पहचान (verification) की जा सके।

    हर session में:
    - session_key (member की पहचान के लिए key)
    - timestamp (session कब बनाया गया)
    शामिल होता है।
    """

    # रोल नंबर के आधार पर session store किया जाता है
    # Format: roll_no -> (session_key, created_time)
    db: dict[int, tuple[str, datetime]] = AuthSessionStore

    @staticmethod
    def get(roll_no: int, default: tuple[str, datetime] | None = None) -> tuple[str, datetime] | None:
        """
        किसी भी roll number के लिए stored session return करता है।

        अगर session मौजूद नहीं है, तो default value return करता है।
        """
        return ES.db.get(roll_no, default)

    @staticmethod
    def add(roll_no: int, key: str) -> tuple[str, datetime]:
        """
        नए member session को memory में store करता है।

        यह method:
        - session_key save करता है
        - current timestamp जोड़ता है
        - और stored session वापस return करता है
        """

        # session बनने का समय
        now = datetime.now()

        # session store करना
        ES.db[roll_no] = (key, now)

        # stored session return करना
        return ES.db[roll_no]
    