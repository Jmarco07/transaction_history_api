from pydantic import BaseModel


class GetIbankFtTransactionResponse(BaseModel):
    result: dict
