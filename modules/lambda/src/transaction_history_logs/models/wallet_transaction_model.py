from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class WalletTransaction(BaseModel):
    ret_ref_id: Optional[str] = None
    trace_id: Optional[str] = None
    amount: Optional[str] = None
    status: Optional[str] = None
    data_1: Optional[str] = None
    data_2: Optional[str] = None
    data_3: Optional[str] = None
    data_4: Optional[str] = None
    data_5: Optional[str] = None
    data_6: Optional[str] = None
    data_7: Optional[str] = None
    data_8: Optional[str] = None
    data_9: Optional[str] = None
    data_10: Optional[str] = None
    data_11: Optional[str] = None
    data_12: Optional[str] = None
    data_13: Optional[str] = None
    data_14: Optional[str] = None
    data_15: Optional[str] = None
    data_16: Optional[str] = None
    data_17: Optional[str] = None
    data_18: Optional[str] = None
    data_19: Optional[str] = None
    data_20: Optional[str] = None
    data_21: Optional[str] = None
    data_22: Optional[str] = None
    data_23: Optional[str] = None
    data_24: Optional[str] = None
    data_25: Optional[str] = None
    data_26: Optional[str] = None
    data_27: Optional[str] = None
    data_28: Optional[str] = None
    data_29: Optional[str] = None
    data_30: Optional[str] = None
    aux_no: Optional[str] = None
    remarks: Optional[str] = None
    insurance_flag: Optional[str] = None
    usr_id: Optional[str] = None
    resp_code: Optional[str] = None
    resp_desc: Optional[str] = None
    last_modified_date: Optional[str] = None
    paye_name: Optional[str] = None
    ref_id: Optional[str] = None
    trfr_mode: Optional[str] = None
    sms_optin_flag: Optional[str] = None
    earned_coupon: Optional[str] = None
    earned_points: Optional[str] = None
    load_datetime: Optional[datetime] = None


class WalletTransactionRequest(BaseModel):
    ret_ref_id: str = Field(..., max_length=500)