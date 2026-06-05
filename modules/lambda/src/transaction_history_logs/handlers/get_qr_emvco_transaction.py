import json
from typing import Any

from handlers.defaults.db import psycopg2_connect
from handlers.defaults.top_level import app
from models.requests.get_qr_emvco_transaction import GetQrEmvcoTransactionRequest
from models.responses.get_qr_emvco_transaction import GetQrEmvcoTransactionResponse
from repositories.qr_emvco_transaction_repository import QrEmvcoTransactionRepository
from utilities.base_response import SuccessResponse
from utilities.request_validator import request_validator

if not hasattr(app, 'CONNECTION'):
    app.CONNECTION = None
    app.CONNECTION_TYPE = None
    print("🚀 Lambda container initializing...")


@request_validator(model=GetQrEmvcoTransactionRequest)
def lambda_handler(event, context) -> dict[str, Any]:
    if event.get("keep_alive"):
        print("💤 Keep-alive ping received. Keeping Lambda warm...")
        try:
            psycopg2_connect(app)
            return {
                'statusCode': 200,
                'body': json.dumps({'status': 'warm', 'message': 'Lambda kept warm'})
            }
        except Exception as e:
            return {
                'statusCode': 503,
                'body': json.dumps({'status': 'cold', 'error': str(e)})
            }

    try:
        psycopg2_connect(app)
    except Exception as e:
        print(f"Connection failed: {e}")
        return {'statusCode': 503, 'body': json.dumps({'error': 'Database connection failed'})}

    body = app.VALIDATED_BODY

    try:
        transaction = QrEmvcoTransactionRepository.get(
            connection=app.CONNECTION,
            get_qr_emvco_transaction_request=body
        )

        if not transaction:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Transaction not found'})
            }

        transaction_data = (
            transaction.model_dump()
            if hasattr(transaction, "model_dump")
            else transaction.__dict__
        )

        response = {"result": {"data": transaction_data}}

        return SuccessResponse(**GetQrEmvcoTransactionResponse(**response).model_dump())

    except Exception as e:
        print(f"Query failed: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': f'Query failed: {str(e)}'})}
