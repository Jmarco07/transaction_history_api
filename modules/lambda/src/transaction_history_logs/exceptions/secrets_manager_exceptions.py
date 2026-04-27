from exceptions.base_exception import CustomException


class SecretRetrievalException(CustomException):
    STATUS_CODE = 500
    ERROR_CODE = "SECRET_RETRIEVAL_EXCEPTION"
    ERROR_MESSAGE = "Secret Retrieval Exception"
    ERROR_DETAILS = "Secret Retrieval Exception"
