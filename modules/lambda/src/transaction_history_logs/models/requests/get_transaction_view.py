from typing import Optional
from pydantic import BaseModel



class GetTransactionViewRequest(BaseModel):
    retRefNo: str