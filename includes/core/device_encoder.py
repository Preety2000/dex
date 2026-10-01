import base64
import zlib
import msgpack

KEYS = {
    "platform": "p",
    "browser": "b",
    "device": "d",
    "platform_version": "pv",
    "browser_version": "bv",
    "is_mobile": "m",
    "is_pc": "pc",
    "is_tablet": "t",
    "is_bot": "bo",
}

REV_KEYS = {v: k for k, v in KEYS.items()}


def encode_device(data: dict) -> str:
    compact = {
        KEYS.get(k, k): v
        for k, v in data.items()
    }

    packed = msgpack.packb(compact, use_bin_type=True)

    compressed = zlib.compress(packed, level=9)

    return base64.urlsafe_b64encode(
        compressed
    ).decode().rstrip("=")


def decode_device(device_id: str) -> dict:
    padding = "=" * (-len(device_id) % 4)

    compressed = base64.urlsafe_b64decode(
        device_id + padding
    )

    packed = zlib.decompress(compressed)

    compact = msgpack.unpackb(
        packed,
        raw=False
    )

    return {
        REV_KEYS.get(k, k): v
        for k, v in compact.items()
    }