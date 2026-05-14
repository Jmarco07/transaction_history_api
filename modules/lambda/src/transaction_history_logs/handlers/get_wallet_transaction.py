import json
import logging
from typing import Dict, Any

from handlers.defaults.db import psycopg2_connect
from handlers.defaults.top_level import app
from models.wallet_transaction_model import WalletTransaction, WalletTransactionRequest
from utilities.base_response import SuccessResponse, ExceptionResponse
from utilities.request_validator import request_validator

logger = logging.getLogger()
logger.setLevel(logging.INFO)

if not hasattr(app, 'CONNECTION'):
    app.CONNECTION = None
    app.CONNECTION_TYPE = None
    print("Lambda container initializing...")


@request_validator(model=WalletTransactionRequest)
def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda handler for wallet transaction history lookup.
    
    Args:
        event: API Gateway event containing the request
        context: Lambda context object
        
    Returns:
        API Gateway response with transaction data or error
    """
    try:
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

        try:
            psycopg2_connect(app)
        except Exception as e:
            print(f"Connection failed: {e}")
            return {'statusCode': 503, 'body': json.dumps({'error': 'Database connection failed'})}
        
        print("Connection state:", "Connected" if app.CONNECTION else "Not connected")
        print("Request:", event)

        request_data = app.VALIDATED_BODY

        query = """
        SELECT 
            ret_ref_id, trace_id, amount, status,
            data_1, data_2, data_3, data_4, data_5, data_6, data_7, data_8, data_9, data_10,
            data_11, data_12, data_13, data_14, data_15, data_16, data_17, data_18, data_19, data_20,
            data_21, data_22, data_23, data_24, data_25, data_26, data_27, data_28, data_29, data_30,
            aux_no, remarks, insurance_flag, usr_id, resp_code, resp_desc, last_modified_date,
            paye_name, ref_id, trfr_mode, sms_optin_flag, earned_coupon, earned_points, load_datetime
        FROM target.megalink_wlt_trxn_hist_fct 
        WHERE ret_ref_id = %s
        LIMIT 1
        """
        
        try:
            app.CONNECTION.CLIENT.rollback()
            
            with app.CONNECTION.CLIENT.cursor() as cursor:
                cursor.execute(query, (request_data.ret_ref_id,))
                result = cursor.fetchone()
                
                if not result:
                    return {
                        'statusCode': 404,
                        'body': json.dumps({'error': 'Transaction not found'})
                    }

                columns = [desc[0] for desc in cursor.description]

                transaction_dict = dict(zip(columns, result))

                wallet_transaction = WalletTransaction(**transaction_dict)

                return SuccessResponse(
                    status_code=200,
                    result={"data": wallet_transaction.model_dump()}
                )
        except Exception as db_error:
            print(f"Database query failed: {str(db_error)}")
            try:
                app.CONNECTION.CLIENT.rollback()
            except:
                pass
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Database query failed'})
            }

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return ExceptionResponse(e)