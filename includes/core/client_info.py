import requests
import socket
from user_agents import parse

from includes.core.device_encoder import encode_device
from includes.core.deviceinfo import DeviceInfo
from includes.core.globals.entry import app_context
from includes.core.security import _Security


# -------------------------
# Safe JSON fetch
# -------------------------
def safe_get_json(url, timeout=5):
    try:
        res = requests.get(url, timeout=timeout)

        if res.status_code != 200:
            return None

        data = res.json()
        return data if isinstance(data, dict) else None

    except (requests.RequestException, ValueError):
        return None


# -------------------------
# Fingerprint generator (FIXED MISSING FUNCTION)
# -------------------------
import hashlib


def generate_fingerprint(ip, ua, lang, timezone):
    raw = f"{ip}|{ua}|{lang}|{timezone}"
    return hashlib.sha256(raw.encode()).hexdigest()


# -------------------------
# Main Function (FIXED + COMPLETE)
# -------------------------
def collect_user_signals(ip):

    # -------------------------
    # Headers (FIXED: consistent variables)
    # -------------------------
    user_agent_string = app_context.request.headers.get("User-Agent", "")
    accept_language = app_context.request.headers.get("Accept-Language", "")
    client_timezone = app_context.request.headers.get("X-Timezone", "")

    DeviceInfo.reset(app_context.request)
    device_info = DeviceInfo.to_dict()
    # -------------------------
    # IP APIs
    # -------------------------
    ipinfo = safe_get_json(f"https://ipinfo.io/{ip}/json") or {}
    ipapi = safe_get_json(f"http://ip-api.com/json/{ip}") or {}

    # -------------------------
    # Hostname
    # -------------------------
    try:
        hostname = socket.gethostbyaddr(ip)[0].lower()
    except:
        hostname = ""

    # -------------------------
    # NETWORK MERGE (ALL VALUES FIXED)
    # -------------------------
    isp = ipinfo.get("org") or ipapi.get("isp") or ""

    city = ipapi.get("city") or ipinfo.get("city")
    region = ipapi.get("regionName") or ipinfo.get("region")
    country = ipapi.get("country") or ipinfo.get("country")
    country_code = ipapi.get("countryCode") or ipinfo.get("country")
    postal = ipapi.get("zip") or ipinfo.get("postal")
    timezone = ipapi.get("timezone") or ipinfo.get("timezone")
    loc = ipinfo.get("loc")

    # -------------------------
    # Connection classification
    # -------------------------
    score = {"mobile": 0, "broadband": 0, "vpn": 0, "datacenter": 0}

    mobile_kw = ["jio", "airtel", "vi", "vodafone", "cellular"]
    broadband_kw = ["fiber", "broadband", "dsl", "internet"]
    dc_kw = ["aws", "amazon", "google", "azure", "digitalocean", "cloud"]

    text = f"{isp} {hostname}".lower()

    if any(k in text for k in mobile_kw):
        score["mobile"] += 3

    if any(k in text for k in broadband_kw):
        score["broadband"] += 2

    if any(k in text for k in dc_kw):
        score["datacenter"] += 3
        score["vpn"] += 2

    if "amazonaws" in hostname or "googleusercontent" in hostname:
        score["datacenter"] += 2
        score["vpn"] += 1

    result = max(score, key=score.get)
    confidence = (score[result] / 5) * 100 if score[result] > 0 else 0

    # -------------------------
    # Risk score (FIXED SAFE)
    # -------------------------
    risk_score = 0

    if not isp:
        risk_score += 20

    if DeviceInfo.device == "Other":
        risk_score += 10

    if "bot" in user_agent_string.lower():
        risk_score += 40

    if not accept_language:
        risk_score += 10

    if result == "datacenter":
        risk_score += 25

    if client_timezone and timezone and client_timezone != timezone:
        risk_score += 10

    risk_score = min(risk_score, 100)

    # -------------------------
    # Fingerprint ID (FIXED VARIABLE)
    # -------------------------
    fingerprint_id = generate_fingerprint(
        ip, user_agent_string, accept_language, timezone or ""
    )

    # -------------------------
    # FINAL OUTPUT (COMPLETE)
    # -------------------------
    return {
        "device_id": encode_device(device_info),
        "fingerprint_id": fingerprint_id,
        "client": {
            "user_agent": user_agent_string,
            "accept_language": accept_language,
            "client_timezone": client_timezone,
        },
        "network": {
            "ip": ip,
            "isp": isp,
            "city": city,
            "region": region,
            "country": country,
            "country_code": country_code,
            "postal": postal,
            "timezone": timezone,
            "loc": loc,
            "hostname": hostname,
        },
        "classification": {
            "connection_type": result,
            "confidence": round(confidence, 2),
            "scores": score,
        },
        "security": {
            "risk_score": risk_score,
            "risk_level": (
                "low" if risk_score < 30 else "medium" if risk_score < 70 else "high"
            ),
        },
    }
