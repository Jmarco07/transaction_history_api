from pydantic import BaseModel, Field


class GetWalletTransactionRequest(BaseModel):
    ret_ref_id: str = Field(..., max_length=500, description="Reference ID to lookup wallet transaction")