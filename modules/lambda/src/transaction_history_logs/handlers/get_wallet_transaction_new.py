import json
from typing import Any

from handlers.defaults.db import psycopg2_connect
from handlers.defaults.top_level import app
from models.requests.get_wallet_transaction import GetWalletTransactionRequest
from models.responses.get_wallet_transaction import GetWalletTransactionResponse
from repositories.wallet_transaction_repository import WalletTransactionRepository
from utilities.base_response import SuccessResponse
from utilities.request_validator import request_validator

if not hasattr(app, 'CONNECTION'):
    app.CONNECTION = None
    app.CONNECTION_TYPE = None
    print("Lambda container initializing...")


@request_validator(model=GetWalletTransactionRequest)
def lambda_handler(event, context) -> dict[str, Any]:
    """
    Lambda handler for wallet transaction history lookup.
    
    Args:
        event: API Gateway event containing the request
        context: Lambda context object
        
    Returns:
        API Gateway response with transaction data or error
    """

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
        wallet_transaction = WalletTransactionRepository.get(
            connection=app.CONNECTION,
            get_wallet_transaction_request=body
        )
        
        if not wallet_transaction:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Transaction not found'})
            }

        transaction_data = (
            wallet_transaction.model_dump() 
            if hasattr(wallet_transaction, "model_dump") 
            else wallet_transaction.__dict__
        )

        response = {
            "result": {"data": transaction_data}
        }
        
        return SuccessResponse(**GetWalletTransactionResponse(**response).model_dump())
        
    except Exception as e:
        print(f"Query failed: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': f'Query failed: {str(e)}'})}