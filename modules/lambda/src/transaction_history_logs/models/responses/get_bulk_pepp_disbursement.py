from typing import Optional, List
from pydantic import BaseModel


class PageInfo(BaseModel):
    hasNextPage: bool
    hasPreviousPage: bool
    startCursor: Optional[str] = None
    endCursor: Optional[str] = None
    totalRecords: int
    totalPages: int


class FinancialSummary(BaseModel):
    totalAmount: float
    totalSuccess: int
    totalFailed: int
    totalClaimedPepp: int
    totalUnclaimedPepp: int


class BulkPeppDisbursementResultDict(BaseModel):
    data: List[dict]


class GetBulkPeppDisbursementResponse(BaseModel):
    result: BulkPeppDisbursementResultDict
    pageInfo: PageInfo
    summary: FinancialSummary
