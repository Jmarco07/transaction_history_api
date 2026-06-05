from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from utilities.date_converter import to_gmt8


class PesonetTransaction(BaseModel):
    add_date: Optional[str] = ""
    aux_no: Optional[str] = ""
    trxn_reference_number: Optional[str] = ""
    trxn_typ: Optional[str] = ""
    trxn_type_desc: Optional[str] = ""
    trx_amt: Optional[str] = ""
    cur_id: Optional[str] = ""
    acc_id: Optional[str] = ""
    ext_rcvr_bnk_id: Optional[str] = ""
    ext_rcvr_bnk_name: Optional[str] = ""
    ext_acc_id: Optional[str] = ""
    stat: Optional[str] = ""
    resp_code: Optional[str] = ""
    resp_desc: Optional[str] = ""
    stat_desc: Optional[str] = ""
    merchant_id: Optional[str] = ""
    msg_id: Optional[str] = ""
    load_datetime: Optional[datetime] = None

    @field_validator("add_date", mode="before")
    @classmethod
    def convert_dates(cls, v):
        return to_gmt8(v)
