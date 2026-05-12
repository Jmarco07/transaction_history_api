from typing import List
from pydantic import BaseModel
from models.wallet_transaction_model import WalletTransaction


class GetWalletTransactionResponse(BaseModel):
    result: dict
    
    class Config:
        json_encoders = {
            # Add any custom encoders if needed
        }