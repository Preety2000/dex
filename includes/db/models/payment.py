from sqlalchemy import BigInteger, Column, Float, Integer, String, Text

from includes.db.models.owner import BaseOwner
from includes.db.models.utils import TimeStamp


class Payment(BaseOwner):

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    merchant_order_id = Column(String(100), unique=True, nullable=False, index=True)
    amount = Column(BigInteger, nullable=False)
    status = Column(String(30), nullable=False, default="PENDING", index=True)
    phonepe_state = Column(String(50), nullable=True)
    redirect_url = Column(Text, nullable=True)
    transaction_id = Column(String(200), nullable=True)
    response_data = Column(Text, nullable=True)
    created_at = Column(TimeStamp, default=TimeStamp.now_iso, nullable=False)
    updated_at = Column(
        TimeStamp, default=TimeStamp.now_iso, onupdate=TimeStamp.now_iso, nullable=False
    )
