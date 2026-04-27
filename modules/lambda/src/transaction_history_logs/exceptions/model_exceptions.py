from exceptions.base_exception import CustomException


class PydanticBaseModelException(CustomException):
    STATUS_CODE = 500
    ERROR_CODE = "PYDANTIC_MODEL_EXCEPTION"
    ERROR_MESSAGE = "Model does not inherit Pydantic Base Model!"
