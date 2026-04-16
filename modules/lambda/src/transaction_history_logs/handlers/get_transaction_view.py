from typing import Any
import json
from datetime import datetime
from decimal import Decimal

from handlers.defaults.db import psycopg2_connect
from handlers.defaults.top_level import app
from models.requests.get_transaction_view import GetTransactionViewRequest
from models.responses.get_transaction_view import TransactionViewResponse
from models.transaction_view_model import TransactionView, FieldItem
from repositories.transaction_view_repository import TransactionViewRepository
from utilities.base_response import SuccessResponse
from utilities.request_validator import request_validator

app.CONNECTION = None
psycopg2_connect(app)


@request_validator(model=GetTransactionViewRequest)
def lambda_handler(event, context) -> dict[str, Any]:
    print("REQUEST:", event)

    ret_ref_id = (event.get("pathParameters") or {}).get("retRefNo") or (event.get("path") or "").rstrip("/").split("/")[-1]
    if not ret_ref_id:
        return _validation_error("transactionNo", "Transaction not found. Please verify the transaction ID.")

    transaction = TransactionViewRepository.get_transaction_view(app.CONNECTION, ret_ref_id)
    if not transaction:
        return _validation_error("transactionNo", "Transaction not found. Please verify the transaction ID.")

    parsed_fields = [
        {"label": field.get("label", ""), "value": field.get("value", "")}
        for field in transaction.get("fields", [])
    ]

    transaction_view = TransactionView(
        fields=[FieldItem(**f) for f in parsed_fields],
        trxn_no=transaction.get("trxn_no"),
        added_date=transaction.get("added_date"),
        service_type=transaction.get("service_type"),
        traceId=transaction.get("traceId"),
        type=transaction.get("type"),
        description=transaction.get("description"),
        cardType=transaction.get("cardType"),
        responseCode=transaction.get("responseCode"),
        amount=transaction.get("amount"),
        gateVariant=transaction.get("gateVariant"),
        status=transaction.get("status"),
        custom_fld=transaction.get("custom_fld"),
    )

    response_model = TransactionViewResponse(result=transaction_view)
    response_data = response_model.model_dump()

    return SuccessResponse(**response_data)


def _validation_error(field: str, message: str) -> dict[str, Any]:
    return {
        "statusCode": 422,
        "body": json.dumps({
            "responseCode": 422,
            "status": "failed",
            "error_code": "REQUEST_VALIDATION_EXCEPTION",
            "error_message": "Request Validation Exception",
            "error_details": [{"field": field, "error": message}],
        }),
        "headers": {"Content-Type": "application/json"},
    }
