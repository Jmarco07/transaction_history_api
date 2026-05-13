from pydantic import BaseModel, Field


class GetQrEmvcoTransactionRequest(BaseModel):
    optnl_16: str = Field(..., max_length=500, description="Primary identifier for the record lookup")
