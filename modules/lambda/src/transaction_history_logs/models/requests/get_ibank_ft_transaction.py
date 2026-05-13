from pydantic import BaseModel, Field


class GetIbankFtTransactionRequest(BaseModel):
    msg_id: str = Field(..., max_length=500, description="Unique message identifier")
    ret_ref_id: str = Field(..., max_length=500, description="Return Reference ID")
