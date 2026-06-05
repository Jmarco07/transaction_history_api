from typing import Optional
from pydantic import BaseModel


class PageInfo(BaseModel):
    hasNextPage: bool
    hasPreviousPage: bool
    startCursor: Optional[str] = None
    endCursor: Optional[str] = None


class CorporateTransactionResultDict(BaseModel):
    data: list[dict]


class GetCorporateTransactionResponse(BaseModel):
    result: CorporateTransactionResultDict
    pageInfo: PageInfo
