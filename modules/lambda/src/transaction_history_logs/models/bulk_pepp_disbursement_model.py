from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from utilities.date_converter import to_gmt8


class BulkPeppDisbursementTransaction(BaseModel):
    company_id: Optional[str] = ""
    filename: Optional[str] = ""
    uploaded_by: Optional[str] = ""
    uploaded_date: Optional[str] = ""
    account_id: Optional[str] = ""
    bulk_id: Optional[str] = ""
    msg_id: Optional[str] = ""
    aux_no: Optional[str] = ""
    claim_code: Optional[str] = ""
    from_account: Optional[str] = ""
    to_account: Optional[str] = ""
    trxn_amt: Optional[str] = ""
    trxn_typ: Optional[str] = ""
    trxn_type_desc: Optional[str] = ""
    receiver_first_name: Optional[str] = ""
    receiver_middle_name: Optional[str] = ""
    receiver_last_name: Optional[str] = ""
    receiver_mobile_no: Optional[str] = ""
    stat_code: Optional[str] = ""
    itrl_usr_msg_code: Optional[str] = ""
    usr_msg_code: Optional[str] = ""
    optional_1: Optional[str] = ""
    optional_2: Optional[str] = ""
    optional_3: Optional[str] = ""
    optional_4: Optional[str] = ""
    optional_5: Optional[str] = ""
    optional_6: Optional[str] = ""
    optional_7: Optional[str] = ""
    optional_8: Optional[str] = ""
    optional_9: Optional[str] = ""
    optional_10: Optional[str] = ""
    optional_11: Optional[str] = ""
    optional_12: Optional[str] = ""
    resp_code: Optional[str] = ""
    upload_status: Optional[str] = ""
    trxn_status: Optional[str] = ""
    trxn_reference_number: Optional[str] = ""
    last_modified_by: Optional[str] = ""
    last_modified_date: Optional[str] = ""
    load_datetime: Optional[datetime] = None

    @field_validator("uploaded_date", "last_modified_date", mode="before")
    @classmethod
    def convert_dates(cls, v):
        return to_gmt8(v)
