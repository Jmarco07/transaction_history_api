import json
from typing import Any

from handlers.defaults.db import psycopg2_connect
from handlers.defaults.top_level import app
from models.requests.get_ibank_ft_transaction import GetIbankFtTransactionRequest
from models.responses.get_ibank_ft_transaction import GetIbankFtTransactionResponse
from repositories.ibank_ft_transaction_repository import IbankFtTransactionRepository
from utilities.base_response import SuccessResponse
from utilities.request_validator import request_validator

if not hasattr(app, 'CONNECTION'):
    app.CONNECTION = None
    app.CONNECTION_TYPE = None
    print("🚀 Lambda container initializing...")


@request_validator(model=GetIbankFtTransactionRequest)
def lambda_handler(event, context) -> dict[str, Any]:
    # Handle keep-alive ping
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

    # Establish database connection
    try:
        psycopg2_connect(app)
    except Exception as e:
        print(f"Connection failed: {e}")
        return {'statusCode': 503, 'body': json.dumps({'error': 'Database connection failed'})}

    body = app.VALIDATED_BODY

    try:
        transaction = IbankFtTransactionRepository.get(
            connection=app.CONNECTION,
            get_ibank_ft_transaction_request=body
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

        response = {"result": transaction_data}

        return SuccessResponse(**GetIbankFtTransactionResponse(**response).model_dump())

    except Exception as e:
        print(f"Query failed: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': f'Query failed: {str(e)}'})}
