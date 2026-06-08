from typing import Optional
from pydantic import BaseModel


class PageInfo(BaseModel):
    hasNextPage: bool
    hasPreviousPage: bool
    startCursor: Optional[str] = None
    endCursor: Optional[str] = None
    totalRecords: int
    totalPages: int


class FinancialSummary(BaseModel):
    totalDrAmount: float
    totalCrAmount: float
    totalSettled: int
    totalReversed: int


class PesonetTransactionResultDict(BaseModel):
    data: list[dict]


class GetPesonetTransactionResponse(BaseModel):
    result: PesonetTransactionResultDict
    pageInfo: PageInfo
    summary: FinancialSummary
