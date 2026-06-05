from pydantic import BaseModel


class QrEmvcoTransactionResultDict(BaseModel):
    data: dict


class GetQrEmvcoTransactionResponse(BaseModel):
    result: QrEmvcoTransactionResultDict
