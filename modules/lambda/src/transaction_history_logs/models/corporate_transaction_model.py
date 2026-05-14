from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CorporateTransaction(BaseModel):
    c_d: Optional[str] = ""
    trx_amt: Optional[str] = ""
    trx_cur: Optional[str] = ""
    trx_stat: Optional[str] = ""
    trx_stat_desc: Optional[str] = ""
    trx_date: Optional[str] = ""
    trx_desc: Optional[str] = ""
    trx_type: Optional[str] = ""
    run_balance: Optional[str] = ""
    ret_ref_id: Optional[str] = ""
    aux_no: Optional[str] = ""
    location: Optional[str] = ""
    dest_account: Optional[str] = ""
    total: Optional[str] = ""
    contract_no: Optional[str] = ""
    source: Optional[str] = ""
    source_account: Optional[str] = ""
    partner_ref_number: Optional[str] = ""
    load_datetime: Optional[datetime] = None
