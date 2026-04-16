from models.transaction_view_model import TransactionView
from pydantic import BaseModel

class TransactionViewResponse(BaseModel):
    result: TransactionView
