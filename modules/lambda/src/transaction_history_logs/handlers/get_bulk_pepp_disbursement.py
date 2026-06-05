import json
from typing import Any

from handlers.defaults.db import psycopg2_connect
from handlers.defaults.top_level import app
from models.requests.get_bulk_pepp_disbursement import GetBulkPeppDisbursementRequest
from models.responses.get_bulk_pepp_disbursement import GetBulkPeppDisbursementResponse
from repositories.bulk_pepp_disbursement_repository import BulkPeppDisbursementRepository
from utilities.base_response import SuccessResponse
from utilities.request_validator import request_validator

if not hasattr(app, 'CONNECTION'):
    app.CONNECTION = None
    app.CONNECTION_TYPE = None
    print("🚀 Lambda container initializing...")


@request_validator(model=GetBulkPeppDisbursementRequest)
def lambda_handler(event, context) -> dict[str, Any]:
    """
    Lambda handler for bulk PEPP disbursement transaction history.
    Supports dynamic filtering and cursor-based pagination.
    """

    # Handle keep-alive ping
    if event.get("keep_alive"):
        print("💤 Keep-alive ping received. Keeping Lambda warm...")
        try:
            psycopg2_connect(app)
            print("Connection active.")
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

    # Establish database connection
    try:
        psycopg2_connect(app)
    except Exception as e:
        print(f"Connection failed: {e}")
        return {'statusCode': 503, 'body': json.dumps({'error': 'Database connection failed'})}

    print("Connection state:", "Connected" if app.CONNECTION else "Not connected")
    print("Request:", event)

    # Get validated request body from the decorator
    body = app.VALIDATED_BODY

    try:
        # Get transactions from repository
        transactions, page_info = BulkPeppDisbursementRepository.get(
            connection=app.CONNECTION,
            get_bulk_pepp_disbursement_request=body
        )

        # Convert to list of dicts
        transactions_data = [
            t.model_dump() if hasattr(t, "model_dump") else t.__dict__
            for t in transactions
        ]

        total_records = len(transactions_data)
        print(f"Fetched {total_records} transactions")

        # Build response
        response = {
            "result": {"data": transactions_data},
            "pageInfo": page_info,
        }

        return SuccessResponse(**GetBulkPeppDisbursementResponse(**response).model_dump())

    except Exception as e:
        print(f"Query failed: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': f'Query failed: {str(e)}'})}
