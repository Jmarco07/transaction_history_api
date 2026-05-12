from typing import Optional
from models.requests.get_wallet_transaction import GetWalletTransactionRequest
from models.wallet_transaction_model import WalletTransaction


class WalletTransactionRepository:
    
    @staticmethod
    def get(connection, get_wallet_transaction_request: GetWalletTransactionRequest) -> Optional[WalletTransaction]:
        """
        Fetch wallet transaction by reference ID from Redshift
        
        Args:
            connection: Database connection object
            get_wallet_transaction_request: Request containing ret_ref_id
            
        Returns:
            WalletTransaction object if found, None otherwise
        """
        
        query = """
        SELECT 
            ret_ref_id, trace_id, amount, status,
            data_1, data_2, data_3, data_4, data_5, data_6, data_7, data_8, data_9, data_10,
            data_11, data_12, data_13, data_14, data_15, data_16, data_17, data_18, data_19, data_20,
            data_21, data_22, data_23, data_24, data_25, data_26, data_27, data_28, data_29, data_30,
            aux_no, remarks, insurance_flag, usr_id, resp_code, resp_desc, last_modified_date,
            paye_name, ref_id, trfr_mode, sms_optin_flag, earned_coupon, earned_points, load_datetime
        FROM megalink_wlt_trxn_hist_fct 
        WHERE ret_ref_id = %s
        LIMIT 1
        """
        
        try:
            # Rollback any existing transaction to clear the connection state
            connection.CLIENT.rollback()
            
            with connection.CLIENT.cursor() as cursor:
                cursor.execute(query, (get_wallet_transaction_request.ret_ref_id,))
                result = cursor.fetchone()
                
                if not result:
                    return None
                
                # Get column names from cursor description
                columns = [desc[0] for desc in cursor.description]
                
                # Convert result to dictionary
                transaction_dict = dict(zip(columns, result))
                
                # Convert to WalletTransaction model
                return WalletTransaction(**transaction_dict)
                
        except Exception as e:
            print(f"Database query failed in WalletTransactionRepository: {str(e)}")
            # Rollback the transaction on error
            try:
                connection.CLIENT.rollback()
            except:
                pass
            raise e