from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class AgentTransaction(BaseModel):
    trxnNo: Optional[str] = None
    retRefNo: Optional[str] = None
    cardNo: Optional[str] = None
    source: Optional[str] = None
    recipient: Optional[str] = None
    amount: Optional[Decimal] = None
    trxnDate: Optional[datetime] = None
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
    addedDate: Optional[datetime] = None
    setlFlag: Optional[str] = None
    statusDes: Optional[str] = None
    insFlag: Optional[str] = None


