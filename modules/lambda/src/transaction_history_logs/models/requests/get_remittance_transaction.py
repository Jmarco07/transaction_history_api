from pydantic import BaseModel, Field


class GetRemittanceTransactionRequest(BaseModel):
    de159: str = Field(..., max_length=500, description="Primary identifier to lookup remittance transaction")