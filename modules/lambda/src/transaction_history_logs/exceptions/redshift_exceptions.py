from exceptions.base_exception import CustomException, SuccessException


class RedshiftConnectionException(CustomException):
    STATUS_CODE = 500
    ERROR_CODE = "REDSHIFT_CONNECTION_ERROR"
    ERROR_MESSAGE = "Redshift Connection Error"
    ERROR_DETAILS = "Redshift Connection Error"


class RedshiftQueryException(CustomException):
    STATUS_CODE = 500
    ERROR_CODE = "REDSHIFT_QUERY_ERROR"
    ERROR_MESSAGE = "Redshift Query Error"
    ERROR_DETAILS = "Redshift Query Error"

class RedshiftActiveQueryException(SuccessException):
    STATUS_CODE = 201
    EXCEPTION_CODE = "REDSHIFT_QUERY_IN_PROGRESS"
    EXCEPTION_MESSAGE = "Redshift Query In Progress"
    EXCEPTION_DETAILS = "Redshift Query In Progress"


class RedshiftAbortedQueryException(SuccessException):
    STATUS_CODE = 202
    EXCEPTION_CODE = "REDSHIFT_QUERY_ABORTED"
    EXCEPTION_MESSAGE = "Redshift Query Aborted"
    EXCEPTION_DETAILS = "Redshift Query Aborted"
