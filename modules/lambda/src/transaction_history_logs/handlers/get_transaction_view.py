from typing import Any
import json

from handlers.defaults.db import psycopg2_connect
from handlers.defaults.top_level import app
from models.requests.get_transaction_view import GetTransactionViewRequest
from models.responses.get_transaction_view import TransactionViewResponse
from models.transaction_view_model import TransactionView
from repositories.transaction_view_repository import TransactionViewRepository
from utilities.base_response import SuccessResponse
from utilities.request_validator import request_validator

if not hasattr(app, 'CONNECTION'):
    app.CONNECTION = None
    app.CONNECTION_TYPE = None


@request_validator(model=GetTransactionViewRequest)
def lambda_handler(event, context) -> dict[str, Any]:

    if event.get("keep_alive"):
        print("Keep-alive ping received. Keeping Lambda warm...")
        try:
            psycopg2_connect(app)
            return {
                'statusCode': 200,
                'body': json.dumps({'status': 'warm', 'message': 'Lambda kept warm'})
            }
        except Exception as e:
            print(f"Keep-alive failed: {e}")
            return {
                'statusCode': 503,
                'body': json.dumps({'status': 'cold', 'error': str(e)})
            }

    try:
        psycopg2_connect(app)
    except Exception as e:
        print(f"Connection failed: {e}")
        return {'statusCode': 503, 'body': json.dumps({'error': 'Database connection failed'})}

    print("REQUEST:", event)

    ret_ref_id = (
        (event.get("pathParameters") or {}).get("retRefNo")
        or (event.get("path") or "").rstrip("/").split("/")[-1]
    )

    print("Extracted transaction ID:", ret_ref_id)

    if not ret_ref_id:
        return _validation_error(
            "transactionNo",
            "Transaction not found. Please verify the transaction ID.",
        )

    transaction = TransactionViewRepository.get_transaction_view(
        app.CONNECTION,
        ret_ref_id,
    )

    if not transaction:
        return _validation_error(
            "transactionNo",
            "Transaction not found. Please verify the transaction ID.",
        )

    transaction_view = TransactionView(**transaction)

    response_model = TransactionViewResponse(result=transaction_view)
    return SuccessResponse(**response_model.model_dump())


def _validation_error(field: str, message: str) -> dict[str, Any]:
    return {
        "statusCode": 422,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {
                "responseCode": 422,
                "status": "failed",
                "error_code": "REQUEST_VALIDATION_EXCEPTION",
                "error_message": "Request Validation Exception",
                "error_details": [{"field": field, "error": message}],
            }
        ),
    }
