from fastapi import requests

def send_otp(mobile: str):
    api_key = ""

    url = (
        f"https://2factor.in/API/V1/"
        f"{api_key}/SMS/{mobile}/AUTOGEN"
    )

    response = requests.get(url, timeout=10)

    print(response.status_code)
    print(response.json())

    return response.json()