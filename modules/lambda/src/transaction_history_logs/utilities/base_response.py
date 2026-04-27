from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from exceptions.base_exception import CustomException, SuccessException


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)


def _cors_response(code: int, body: Any):
    return {
        "statusCode": code,
        "content_type": "application/json",
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Header": "*",
        },
        "body": body,
    }


def ErrorResponse(error: CustomException):
    err = {
        "responseCode": error.STATUS_CODE,
        "status": "failed",
        "error_code": error.ERROR_CODE,
        "error_message": error.ERROR_MESSAGE,
    }

    if hasattr(error, "ERROR_DETAILS"):
        err["error_details"] = error.ERROR_DETAILS

    return _cors_response(
        code=error.STATUS_CODE,
        body=json.dumps(err),
    )


def ExceptionResponse(error: Exception):
    err = {
        "responseCode": 500,
        "status": "failed",
        "error_code": "SERVER_ERROR",
        "error_message": "Server Error.",
        "error_details": str(error),
    }

    return _cors_response(
        code=500,
        body=json.dumps(err),
    )


def SuccessExceptionResponse(exception: SuccessException):
    err = {
        "responseCode": exception.STATUS_CODE,
        "status": "exception",
        "exception_code": exception.EXCEPTION_CODE,
        "exception_message": exception.EXCEPTION_MESSAGE,
    }

    if hasattr(exception, "EXCEPTION_DETAILS"):
        err["exception_details"] = exception.EXCEPTION_DETAILS

    return _cors_response(
        code=exception.STATUS_CODE,
        body=json.dumps(err),
    )


def SuccessResponse(status_code: int = 200, **other_data: dict[Any, Any]):
    response = {"responseCode": status_code, "status": "success", **other_data}

    return _cors_response(
        code=200,
        body=json.dumps(response, cls=DecimalEncoder),
    )
