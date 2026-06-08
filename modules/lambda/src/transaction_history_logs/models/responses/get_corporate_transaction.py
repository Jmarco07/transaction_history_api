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


class CorporateTransactionResultDict(BaseModel):
    data: list[dict]


class GetCorporateTransactionResponse(BaseModel):
    result: CorporateTransactionResultDict
    pageInfo: PageInfo
    summary: FinancialSummary
