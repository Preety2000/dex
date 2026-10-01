import time
from typing import Any

import httpx

from includes.core.config import settings


class PhonePeError(Exception):
    pass


class PhonePeService:

    def __init__(self):

        self.client = httpx.AsyncClient(
            timeout=30.0
        )

        self.access_token: str | None = None
        self.token_expiry: int = 0

    async def close(self):

        await self.client.aclose()

    async def get_access_token(self) -> str:

        now = int(time.time())

        # Existing token अभी valid है
        if (
            self.access_token
            and now < self.token_expiry - 60
        ):
            return self.access_token

        data = {
            "client_id": settings.PHONEPE_CLIENT_ID,
            "client_version": settings.PHONEPE_CLIENT_VERSION,
            "client_secret": settings.PHONEPE_CLIENT_SECRET,
            "grant_type": "client_credentials",
        }

        response = await self.client.post(
            settings.phonepe_auth_url,
            data=data,
            headers={
                "Content-Type":
                    "application/x-www-form-urlencoded"
            },
        )

        if response.status_code >= 400:
            raise PhonePeError(
                f"Authentication failed: "
                f"{response.text}"
            )

        result = response.json()

        token = result.get("access_token")

        if not token:
            raise PhonePeError(
                "PhonePe access_token missing"
            )

        self.access_token = token

        expires_at = result.get("expires_at")

        if expires_at:
            self.token_expiry = int(expires_at)
        else:
            self.token_expiry = now + 300

        return token

    async def create_payment(
        self,
        merchant_order_id: str,
        amount: int,
        redirect_url: str,
    ) -> dict[str, Any]:

        token = await self.get_access_token()

        payload = {
            "merchantOrderId": merchant_order_id,
            "amount": amount,
            "paymentFlow": {
                "type": "PG_CHECKOUT"
            },
            "expireAfter": 1200,
            "redirectUrl": redirect_url,
        }

        response = await self.client.post(

            f"{settings.phonepe_base_url}"
            "/checkout/v2/pay",

            json=payload,

            headers={
                "Content-Type": "application/json",
                "Authorization": f"O-Bearer {token}",
            },
        )

        if response.status_code >= 400:

            raise PhonePeError(
                f"Payment creation failed: "
                f"{response.text}"
            )

        return response.json()

    async def get_order_status(
        self,
        merchant_order_id: str,
    ) -> dict[str, Any]:

        token = await self.get_access_token()

        url = (
            f"{settings.phonepe_base_url}"
            f"/checkout/v2/order/"
            f"{merchant_order_id}/status"
        )

        response = await self.client.get(

            url,

            headers={
                "Authorization": f"O-Bearer {token}",
            },
        )

        if response.status_code >= 400:

            raise PhonePeError(
                f"Status request failed: "
                f"{response.text}"
            )

        return response.json()


phonepe_service = PhonePeService()