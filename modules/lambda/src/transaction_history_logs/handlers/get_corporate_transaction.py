import json
from typing import Any

from handlers.defaults.db import psycopg2_connect
from handlers.defaults.top_level import app
from models.requests.get_corporate_transaction import GetCorporateTransactionRequest
from models.responses.get_corporate_transaction import GetCorporateTransactionResponse
from repositories.corporate_transaction_repository import CorporateTransactionRepository
from utilities.base_response import SuccessResponse
from utilities.request_validator import request_validator

if not hasattr(app, 'CONNECTION'):
    app.CONNECTION = None
    app.CONNECTION_TYPE = None
    print("🚀 Lambda container initializing...")


@request_validator(model=GetCorporateTransactionRequest)
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
        transactions, page_info = CorporateTransactionRepository.get(
            connection=app.CONNECTION,
            request=body
        )

        transaction_data = [
            t.model_dump() if hasattr(t, "model_dump") else t.__dict__
            for t in transactions
        ]

        total_dr = sum(float(t.trx_amt or 0) for t in transactions if t.c_d and t.c_d.strip() == "DR")
        total_cr = sum(float(t.trx_amt or 0) for t in transactions if t.c_d and t.c_d.strip() == "CR")

        response = {
            "result": {"data": transaction_data},
            "pageInfo": page_info,
            "totalDrAmount": total_dr,
            "totalCrAmount": total_cr,
        }

        return SuccessResponse(**GetCorporateTransactionResponse(**response).model_dump())

    except Exception as e:
        print(f"Query failed: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': f'Query failed: {str(e)}'})}
