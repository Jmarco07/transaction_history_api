from datetime import datetime
from decimal import Decimal
from typing import ClassVar

from pydantic import BaseModel, Field


class Transaction(BaseModel):
    trxnNo: str | None
    retrRefNo: str
    trxnType: str
    amount: Decimal
    drCr: str | None
    trxnStatus: str
    trxnDate: datetime
    source: str | None
    recipient: str | None
    cardNo: str | None
    currency: str | None
    debitTrxn: str | None
    creditTrxn: str | None
    description: str | None
    serviceType: str | None
    trxnTypeNo: str | None
    traceNo: str | None
    currencyCode: str | None
    merchant_id: str | None
    walletId: str | None
    senderName: str | None
    terminalId: str | None
    processedBy: str | None
    addedDate: str | None
    setlFlag: str | None
    statusDes: str | None
    insFlag: str | None