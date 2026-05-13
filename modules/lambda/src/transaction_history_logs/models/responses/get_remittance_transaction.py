from pydantic import BaseModel


class GetRemittanceTransactionResponse(BaseModel):
    result: dict
    
    class Config:
        json_encoders = {
            # Add any custom encoders if needed
        }