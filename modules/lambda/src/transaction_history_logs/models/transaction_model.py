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



class CorporateTransaction(BaseModel):
    fileName: Optional[str] = None
    uploadedBy: Optional[str] = None
    uploadedDate: Optional[str] = None
    acctNo: Optional[str] = None
    bulkId: Optional[str] = None
    auxNo: Optional[str] = None
    claimCode: Optional[str] = None
    fromAcct: Optional[str] = None
    toAcct: Optional[str] = None
    trxnAmount: Optional[Decimal] = None
    trxnDesc: Optional[str] = None
    firstName: Optional[str] = None
    middleName: Optional[str] = None
    lastName: Optional[str] = None
    mobileNo: Optional[str] = None
    optional1: Optional[str] = None
    optional2: Optional[str] = None
    optional3: Optional[str] = None
    optional4: Optional[str] = None
    optional5: Optional[str] = None
    optional6: Optional[str] = None
    optional7: Optional[str] = None
    optional8: Optional[str] = None
    optional9: Optional[str] = None
    optional10: Optional[str] = None
    optional11: Optional[str] = None
    optional12: Optional[str] = None
    respCode: Optional[str] = None
    uploadStat: Optional[str] = None
    trxnRefNo: Optional[str] = None
    transactionType: Optional[str] = None

