import json
from typing import Any

from handlers.defaults.db import psycopg2_connect
from handlers.defaults.top_level import app
from models.requests.get_remittance_transaction import GetRemittanceTransactionRequest
from models.responses.get_remittance_transaction import GetRemittanceTransactionResponse
from repositories.remittance_transaction_repository import RemittanceTransactionRepository
from utilities.base_response import SuccessResponse
from utilities.request_validator import request_validator

if not hasattr(app, 'CONNECTION'):
    app.CONNECTION = None
    app.CONNECTION_TYPE = None
    print("🚀 Lambda container initializing...")


@request_validator(model=GetRemittanceTransactionRequest)
def lambda_handler(event, context) -> dict[str, Any]:
    """
    Lambda handler for remittance transaction history lookup.
    
    Args:
        event: API Gateway event containing the request
        context: Lambda context object
        
    Returns:
        API Gateway response with transaction data or error
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
        # Get remittance transaction from repository
        remittance_transaction = RemittanceTransactionRepository.get(
            connection=app.CONNECTION,
            get_remittance_transaction_request=body
        )
        
        if not remittance_transaction:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Transaction not found'})
            }
        
        # Convert to dict for response
        transaction_data = (
            remittance_transaction.model_dump() 
            if hasattr(remittance_transaction, "model_dump") 
            else remittance_transaction.__dict__
        )
        
        # Build response - return the transaction data directly as per the sample JSON
        response = {
            "result": transaction_data
        }
        
        return SuccessResponse(**GetRemittanceTransactionResponse(**response).model_dump())
        
    except Exception as e:
        print(f"Query failed: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': f'Query failed: {str(e)}'})}