from typing import Optional, Any
from datetime import datetime

from pydantic import BaseModel


class TransactionView(BaseModel):
    trxnNo: Optional[str] = None
    trxnTypeNature: Optional[str] = None
    trxnTypeDescription: Optional[str] = None
    amount: Optional[str] = None
    convertedAmount: Optional[str] = None
    fees: Optional[str] = None
    receiverCountry: Optional[str] = None
    remittancePartner: Optional[str] = None
    deliveryMethod: Optional[str] = None
    location: Optional[str] = None
    pin: Optional[str] = None
    item: Optional[str] = None
    date: Optional[Any] = None
    pawnTicketNo: Optional[str] = None
    bulkRefNo: Optional[str] = None
    traceNo: Optional[str] = None
    orderNo: Optional[str] = None
    biller: Optional[str] = None
    product: Optional[str] = None
    fee: Optional[str] = None
    senderFrom: Optional[str] = None
    discount: Optional[str] = None
    totalAmount: Optional[str] = None
    merchant: Optional[str] = None
    provider: Optional[str] = None
    sku: Optional[str] = None
    acctNo: Optional[str] = None
    acctNoMobileNo: Optional[str] = None
    recipient: Optional[str] = None
    recipientName: Optional[str] = None
    claimCode: Optional[str] = None
    recipientNo: Optional[str] = None
    partner: Optional[str] = None
    protektodoPackage: Optional[str] = None
    policyHolder: Optional[str] = None
    toAccount: Optional[str] = None
    loyaltyNo: Optional[str] = None
    source: Optional[str] = None
    receiver: Optional[str] = None
    account: Optional[str] = None
    purpose: Optional[str] = None
    sender: Optional[str] = None
    senderAccountName: Optional[str] = None
    status: Optional[str] = None
    refCardId: Optional[str] = None
    transactionId: Optional[str] = None
    token: Optional[str] = None
    bank: Optional[str] = None
