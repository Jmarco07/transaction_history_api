from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, field_validator
from utilities.date_converter import to_gmt8


class AgentTransaction(BaseModel):
    trxnNo: Optional[str] = None
    retRefNo: Optional[str] = None
    cardNo: Optional[str] = None
    source: Optional[str] = None
    recipient: Optional[str] = None
    amount: Optional[Decimal] = None
    trxnDate: Optional[str] = None
    currency: Optional[str] = None
    debitTrxn: Optional[float] = None
    creditTrxn: Optional[float] = None
    drCr: Optional[str] = None
    description: Optional[str] = None
    serviceType: Optional[str] = None
    trxnTypeNo: Optional[str] = None
    traceNo: Optional[str] = None
    currencyCode: Optional[str] = None
    merchant_id: Optional[str] = None
    walletId: Optional[str] = None
    senderName: Optional[str] = None
    terminalId: Optional[str] = None
    processedBy: Optional[str] = None
    addedDate: Optional[str] = None
    setlFlag: Optional[str] = None
    statusDes: Optional[str] = None
    insFlag: Optional[str] = None

    @field_validator("trxnDate", "addedDate", mode="before")
    @classmethod
    def convert_dates(cls, v):
        return to_gmt8(v)


