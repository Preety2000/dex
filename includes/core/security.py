import ast
import base64
import json
import zlib
from cryptography.fernet import Fernet


class AUTH_TOKEN:
    @staticmethod
    def get_key(index=0):
        # Replace this with your own implementation
        return "your_key"

    @classmethod
    def reversed(cls, string):
        parts = string.split("/")

        if len(parts) == 2:
            return parts[1]
        else:
            parts.insert(0, cls.get_key(0))
            return "/".join(parts)

    @classmethod
    def encode(cls, data):
        # Convert object to JSON
        json_data = json.dumps(data, separators=(",", ":"), ensure_ascii=False)

        # Base64 encode
        encoded = base64.b64encode(json_data.encode("utf-8")).decode("utf-8")

        # Remove "=" padding
        encoded = encoded.rstrip("=")

        return cls.reversed(encoded)

    @classmethod
    def decode(cls, _token):
        if not _token:
            return None

        try:
            _token = cls.reversed(_token)

            # Restore padding
            _token += "=" * ((4 - len(_token) % 4) % 4)

            decoded = base64.b64decode(_token).decode("utf-8")

            return json.loads(decoded)

        except Exception as e:
            print("Invalid _token:", e)
            return None




# Generate once (store securely in real apps)
cipher_suite = Fernet(Fernet.generate_key())


class _Security:
    
    @staticmethod
    def r_options(text, encrypt=False):
        mapping = {"/": "1TM5AL70","=": "0TX5SL50"}

        if encrypt:
            for k, v in mapping.items():
                text = text.replace(k, v)
        else:
            for k, v in mapping.items():
                text = text.replace(v, k)

        return text

    # 🔐 Encryption / Decryption
    @staticmethod
    def text_to_encrypted(text: str) -> str:
        encrypted = cipher_suite.encrypt(text.encode()).decode()
        return _Security.r_options(encrypted, True)

    @staticmethod
    def encrypted_to_text(encrypted_text: str) -> str:
        encrypted_text = _Security.r_options(encrypted_text, False)
        return cipher_suite.decrypt(encrypted_text.encode()).decode()

    # 🔢 Text <-> Number
    @staticmethod
    def text_to_number(text: str) -> int:
        return int.from_bytes(text.encode(), 'big')

    @staticmethod
    def number_to_text(number: int) -> str:
        return number.to_bytes((number.bit_length() + 7) // 8, 'big').decode()

    # 📦 Compression
    @staticmethod
    def text_compressed(text: str) -> str:
        compressed = zlib.compress(text.encode(), level=6)  # faster than default 9
        encoded = base64.b64encode(compressed).decode()
        return _Security.r_options(encoded, True)

    @staticmethod
    def text_dcompressed(text: str) -> str:
        text = _Security.r_options(text, False)
        return zlib.decompress(base64.b64decode(text)).decode()

    # 🔤 Custom Encode (hex)
    @staticmethod
    def custom_text_encoded(text: str) -> str:
        return text.encode().hex()  # faster

    @staticmethod
    def custom_text_decode(encoded: str) -> str:
        return bytes.fromhex(encoded).decode()

    # 🔢 Number Encode
    @staticmethod
    def number_encode(number: int) -> str:
        b = number.to_bytes((number.bit_length() + 7) // 8, 'big')
        return base64.urlsafe_b64encode(b).decode().rstrip("=")

    @staticmethod
    def number_decode(string: str) -> int:
        string += "=" * (-len(string) % 4)  # correct padding
        return int.from_bytes(base64.urlsafe_b64decode(string), 'big')



    @staticmethod
    def dict_encode(data: dict) -> str:
        raw = json.dumps(data,separators=(",", ":")).encode()

        compressed = zlib.compress(raw, 9)
        return base64.urlsafe_b64encode(compressed ).decode().rstrip("=")

    @staticmethod
    def dict_decode(id: str) -> dict:
        padding = "=" * (-len(id) % 4)

        compressed = base64.urlsafe_b64decode(id + padding)
        raw = zlib.decompress(compressed)

        return json.loads(raw)


    # ⚡ Short Encode
    @staticmethod
    def short_encode(query):
        if not query:
            return query

        if not isinstance(query, str):
            query = str(query)
            
        num = _Security.text_to_number(query)
        return _Security.number_encode(num)

    @staticmethod
    def short_decode(query):
        query = _Security.number_decode(query)
        query = _Security.number_to_text(query)

        try:
            return int(query)
        except (ValueError, TypeError):
            pass

        try:
            return float(query)
        except (ValueError, TypeError):
            pass


        try:
            result = ast.literal_eval(query)
            if isinstance(result, (list, tuple, dict, bool, type(None))):
                return result
        except (ValueError, SyntaxError, TypeError):
            pass

        
        return query