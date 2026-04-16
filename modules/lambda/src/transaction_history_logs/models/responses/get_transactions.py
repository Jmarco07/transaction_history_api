from typing import Union
from pydantic import BaseModel, Field
from models.transaction_model import AgentTransaction, CorporateTransaction


class GetTransactionsResultDict(BaseModel):
    data: list[Union[AgentTransaction, CorporateTransaction]]


class GetTransactionsResponse(BaseModel):
    limit: int
    offset: int
    result: GetTransactionsResultDict
