from decimal import Decimal
from typing import Optional, List, Union
from datetime import datetime

from pydantic import BaseModel


class FieldItem(BaseModel):
    label: Optional[str]
    value: Optional[Union[str, Decimal]]


class TransactionView(BaseModel):
    fields: Optional[List[FieldItem]] = None
    trxn_no: Optional[str] = None
    added_date: Optional[datetime] = None
    service_type: Optional[str] = None
    traceId: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    cardType: Optional[str] = None
    responseCode: Optional[int] = None
    amount: Optional[Decimal] = None
    gateVariant: Optional[str] = None
    status: Optional[str] = None
    custom_fld: Optional[str] = None
