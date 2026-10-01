from pydantic import BaseModel, Field


class CreatePaymentRequest(BaseModel):
    amount: int = Field(gt=0, description="Amount in paise")


class CreatePaymentResponse(BaseModel):
    merchant_order_id: str
    amount: int
    status: str
    redirect_url: str


class PaymentStatusResponse(BaseModel):
    merchant_order_id: str
    amount: int
    status: str
    phonepe_state: str | None = None
    transaction_id: str | None = None
