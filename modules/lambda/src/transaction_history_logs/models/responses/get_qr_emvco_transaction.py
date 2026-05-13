from pydantic import BaseModel


class GetQrEmvcoTransactionResponse(BaseModel):
    result: dict
