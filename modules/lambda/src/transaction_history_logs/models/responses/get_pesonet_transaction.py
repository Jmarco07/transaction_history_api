from typing import Optional
from pydantic import BaseModel


class PageInfo(BaseModel):
    hasNextPage: bool
    hasPreviousPage: bool
    startCursor: Optional[str] = None
    endCursor: Optional[str] = None


class PesonetTransactionResultDict(BaseModel):
    data: list[dict]


class GetPesonetTransactionResponse(BaseModel):
    result: PesonetTransactionResultDict
    pageInfo: PageInfo
