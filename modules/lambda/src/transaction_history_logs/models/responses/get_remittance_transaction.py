from pydantic import BaseModel


class GetRemittanceTransactionResponse(BaseModel):
    result: dict
    
    class Config:
        json_encoders = {
        }