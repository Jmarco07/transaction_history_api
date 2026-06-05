from pydantic import BaseModel


class IbankFtTransactionResultDict(BaseModel):
    data: dict


class GetIbankFtTransactionResponse(BaseModel):
    result: IbankFtTransactionResultDict
