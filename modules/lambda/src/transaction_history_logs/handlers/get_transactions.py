from typing import Any
import json
import boto3
import csv
from io import StringIO
from datetime import datetime

from handlers.defaults.db import psycopg2_connect
from handlers.defaults.top_level import app
from models.requests.get_transactions import GetTransactionsRequest
from models.responses.get_transactions import GetTransactionsResponse
from repositories.transaction_repository import TransactionRepository
from utilities.base_response import SuccessResponse
from utilities.request_validator import request_validator

S3_BUCKET = "ppay-redshift-api-tfstate-bucket-uat"

s3_client = boto3.client("s3")

if not hasattr(app, 'CONNECTION'):
    app.CONNECTION = None
    app.CONNECTION_TYPE = None
    print("Lambda container initializing...")

@request_validator(model=GetTransactionsRequest)
def lambda_handler(event, context) -> dict[str, Any]:

    if event.get("keep_alive"):
        print("Keep-alive ping received. Keeping Lambda warm...")
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

    try:
        psycopg2_connect(app)
    except Exception as e:
        print(f"Connection failed: {e}")
        return {'statusCode': 503, 'body': json.dumps({'error': 'Database connection failed'})}

    print("Connection state:", "Connected" if app.CONNECTION else "Not connected")
    print("Request:", event)

    body = app.VALIDATED_BODY

    try:
        transactions, page_info = TransactionRepository.get(
            connection=app.CONNECTION,
            get_transactions_request=body
        )

        transactions = [
            t.model_dump() if hasattr(t, "model_dump") else t.__dict__
            for t in transactions
        ]

        total_records = len(transactions)
        print(f"Fetched {total_records} transactions")

        if total_records > 1000:
            print("Uploading results to S3...")

            csv_buffer = StringIO()
            writer = csv.DictWriter(csv_buffer, fieldnames=transactions[0].keys())
            writer.writeheader()
            writer.writerows(transactions)

            filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            s3_client.put_object(Bucket=S3_BUCKET, Key=filename, Body=csv_buffer.getvalue())

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'success',
                    'records': total_records,
                    's3_file': f"s3://{S3_BUCKET}/{filename}"
                })
            }

        response = {
            "result": {"data": transactions},
            "limit": body.limit,
            "pageInfo": page_info,
        }
        return SuccessResponse(**GetTransactionsResponse(**response).model_dump())

    except Exception as e:
        print(f"Query failed: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': f'Query failed: {str(e)}'})}
