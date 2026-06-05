from pydantic import BaseModel


class TransactionViewResultDict(BaseModel):
    data: dict


class TransactionViewResponse(BaseModel):
    result: TransactionViewResultDict
