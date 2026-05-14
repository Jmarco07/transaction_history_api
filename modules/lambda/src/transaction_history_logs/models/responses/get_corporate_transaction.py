from typing import Optional
from pydantic import BaseModel


class PageInfo(BaseModel):
    hasNextPage: bool
    hasPreviousPage: bool
    startCursor: Optional[str] = None
    endCursor: Optional[str] = None


class GetCorporateTransactionResponse(BaseModel):
    result: list[dict]
    pageInfo: PageInfo
