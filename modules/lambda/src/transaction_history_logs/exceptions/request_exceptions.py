from exceptions.base_exception import CustomException


class RequestValidationException(CustomException):
    STATUS_CODE = 422
    ERROR_CODE = "REQUEST_VALIDATION_EXCEPTION"
    ERROR_MESSAGE = "Request Validation Exception"
    ERROR_DETAILS = "Invalid request body"


class BadRequestException(CustomException):
    STATUS_CODE = 400
    ERROR_CODE = "BAD_REQUEST"
    ERROR_MESSAGE = "Bad Request"


class UnauthorizedException(CustomException):
    STATUS_CODE = 401
    ERROR_CODE = "UNAUTHORIZED_EXCEPTION"
    ERROR_MESSAGE = "Unauthorized"
    ERROR_DETAILS = "Unauthorized"
