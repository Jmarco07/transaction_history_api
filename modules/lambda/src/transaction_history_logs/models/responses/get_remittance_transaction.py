from pydantic import BaseModel


class RemittanceTransactionResultDict(BaseModel):
    data: dict


class GetRemittanceTransactionResponse(BaseModel):
    result: RemittanceTransactionResultDict
    
    class Config:
        json_encoders = {
        }