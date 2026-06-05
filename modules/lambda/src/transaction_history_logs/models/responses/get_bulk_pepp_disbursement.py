from typing import Optional, List
from pydantic import BaseModel
from models.bulk_pepp_disbursement_model import BulkPeppDisbursementTransaction


class PageInfo(BaseModel):
    hasNextPage: bool
    hasPreviousPage: bool
    startCursor: Optional[str] = None
    endCursor: Optional[str] = None


class BulkPeppDisbursementResultDict(BaseModel):
    data: List[dict]


class GetBulkPeppDisbursementResponse(BaseModel):
    result: BulkPeppDisbursementResultDict
    pageInfo: PageInfo
