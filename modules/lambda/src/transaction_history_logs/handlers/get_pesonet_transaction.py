import json
from typing import Any

from handlers.defaults.db import psycopg2_connect
from handlers.defaults.top_level import app
from models.requests.get_pesonet_transaction import GetPesonetTransactionRequest
from models.responses.get_pesonet_transaction import GetPesonetTransactionResponse
from repositories.pesonet_transaction_repository import PesonetTransactionRepository
from utilities.base_response import SuccessResponse
from utilities.request_validator import request_validator

if not hasattr(app, 'CONNECTION'):
    app.CONNECTION = None
    app.CONNECTION_TYPE = None
    print("🚀 Lambda container initializing...")


@request_validator(model=GetPesonetTransactionRequest)
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
        transactions, page_info = PesonetTransactionRepository.get(
            connection=app.CONNECTION,
            request=body
        )

        summary = PesonetTransactionRepository.get_summary(
            connection=app.CONNECTION,
            request=body
        )

        transaction_data = [
            t.model_dump() if hasattr(t, "model_dump") else t.__dict__
            for t in transactions
        ]

        response = {
            "result": {"data": transaction_data},
            "pageInfo": {
                **page_info,
                "totalRecords": summary["totalRecords"],
                "totalPages": summary["totalPages"],
            },
            "summary": {
                "totalDrAmount": summary["totalDrAmount"],
                "totalCrAmount": summary["totalCrAmount"],
                "totalSettled": summary["totalSettled"],
                "totalReversed": summary["totalReversed"],
            },
        }

        return SuccessResponse(**GetPesonetTransactionResponse(**response).model_dump())

    except Exception as e:
        print(f"Query failed: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': f'Query failed: {str(e)}'})}
