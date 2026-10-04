from typing import Optional
from fastapi import Request

from includes.utils._sub import configure_page
from includes.core.globals.entry import app_context
from includes.core.globals.initialize import initialize_database
from includes.schemas.payment import (
    CreatePaymentRequest,
    CreatePaymentResponse,
    PaymentStatusResponse,
)


import json
import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session
from includes.core.config import settings
from includes.services.phonepe import PhonePeError, phonepe_service
from includes.database.models.payment import Payment

# from app.app_context.db.database import get_db

payment_router = APIRouter(
    prefix="/api/payment",
    tags=["Payment"],
)


@payment_router.post(
    "/create",
    response_model=CreatePaymentResponse,
)
async def create_payment(request: CreatePaymentRequest):

    # Unique merchant order ID
    merchant_order_id = "ORD_" + uuid.uuid4().hex.upper()

    redirect_url = (
        f"{settings.BACKEND_URL}" f"/api/payment/redirect/" f"{merchant_order_id}"
    )

    payment = Payment(
        merchant_order_id=merchant_order_id,
        amount=request.amount,
        status="PENDING",
    )

    app_context.db.add(payment)

    app_context.db.commit()

    try:

        result = await phonepe_service.create_payment(
            merchant_order_id=merchant_order_id,
            amount=request.amount,
            redirect_url=redirect_url,
        )

        # PhonePe response से redirect URL
        redirect_url_from_phonepe = result.get("redirectUrl") or result.get(
            "redirect_url"
        )

        if not redirect_url_from_phonepe:

            raise PhonePeError("PhonePe redirect URL not found")

        payment.redirect_url = redirect_url_from_phonepe

        payment.response_data = json.dumps(result)

        app_context.db.commit()

        return CreatePaymentResponse(
            merchant_order_id=merchant_order_id,
            amount=request.amount,
            status="PENDING",
            redirect_url=redirect_url_from_phonepe,
        )

    except Exception as exc:

        payment.status = "FAILED"

        payment.response_data = str(exc)

        app_context.db.commit()

        raise HTTPException(
            status_code=502,
            detail="Unable to create payment",
        )


@payment_router.get(
    "/status/{merchant_order_id}",
    response_model=PaymentStatusResponse,
)
async def payment_status(
    merchant_order_id: str,
):

    payment = (
        app_context.db.query(Payment)
        .filter(Payment.merchant_order_id == merchant_order_id)
        .first()
    )

    if not payment:

        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    try:

        result = await phonepe_service.get_order_status(merchant_order_id)

        state = result.get("state")

        if state == "COMPLETED":

            payment.status = "SUCCESS"

        elif state == "FAILED":

            payment.status = "FAILED"

        else:

            payment.status = "PENDING"

        payment.phonepe_state = state

        payment.response_data = json.dumps(result)

        # Payment attempt से transaction ID
        attempts = result.get("paymentDetails", [])

        if attempts:

            latest = attempts[-1]

            payment.transaction_id = latest.get("transactionId")

        app_context.db.commit()

        return PaymentStatusResponse(
            merchant_order_id=merchant_order_id,
            amount=payment.amount,
            status=payment.status,
            phonepe_state=payment.phonepe_state,
            transaction_id=payment.transaction_id,
        )

    except PhonePeError as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )


@payment_router.get("/redirect/{merchant_order_id}")
async def payment_redirect(
    merchant_order_id: str,
):

    return {
        "message": "Payment redirect received",
        "merchant_order_id": merchant_order_id,
        "next": (f"{settings.FRONTEND_URL}" f"/payment/result/" f"{merchant_order_id}"),
    }


async def process_payment():
    # scope_type/scope_slug/resource_type/resource_slug/sub_action/child_entity/modifier
    await initialize_database()

    """Active exam database"""
    await app_context.db.configure_exam()

    if app_context.route.scope_slug and app_context.route.scope_slug in (
        "teacher-basic",
        "teacher-standard",
    ):
        configure_page(template="payment/amount", title="Payment", suffix=True)
        return

    if app_context.route.scope_type == "plan":
        # await Payment.plan(app_context.route.scope_slug, detail)
        configure_page(template="payment/plans", title="Payment", suffix=True)

        return

    # if app_context.route.scope_type == "subscription":
    #     return await Payment.subscription(app_context.route.scope_slug, detail)

    # if app_context.route.scope_type == "payment":
    #     return await Payment.payment(app_context.route.scope_slug, detail)

    # if app_context.route.scope_type == "status":
    #     return await Payment.status(app_context.route.scope_slug, detail)

    # if app_context.route.scope_type == "renew":
    #     return await Payment.renew(app_context.route.scope_slug, detail)

    return {"error": "app_context.route.scope_type not found"}
