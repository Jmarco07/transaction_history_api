from typing import Optional
from models.requests.get_remittance_transaction import GetRemittanceTransactionRequest
from models.remittance_transaction_model import RemittanceTransaction


class RemittanceTransactionRepository:
    
    @staticmethod
    def get(connection, get_remittance_transaction_request: GetRemittanceTransactionRequest) -> Optional[RemittanceTransaction]:
        """
        Fetch remittance transaction by de159 identifier from Redshift
        
        Args:
            connection: Database connection object
            get_remittance_transaction_request: Request containing de159
            
        Returns:
            RemittanceTransaction object if found, None otherwise
        """

        query = """
        SELECT 
            de1, de3, de4, de5, de6, de7, de8, de9, de10,
            de11, de12, de13, de14, de15, de16, de17, de18, de19, de20,
            de21, de22, de23, de24, de25, de26, de27, de28, de29, de30,
            de31, de32, de33, de34, de35, de36, de37, de38, de39, de40,
            de41, de42, de43, de44, de45, de46, de47, de48, de49, de50,
            de51, de52, de53, de54, de55, de56, de57, de58, de59, de60,
            de61, de62, de63, de64, de65, de66, de67, de68, de69, de70,
            de71, de72, de73, de74, de75, de76, de77, de78, de79, de80,
            de81, de82, de83, de84, de85, de86, de87, de88, de89, de90,
            de91, de92, de93, de94, de95, de96, de97, de98, de99, de100,
            de101, de102, de103, de104, de105, de106, de107, de108, de109, de110,
            de111, de112, de113, de114, de115, de116, de117, de118, de119, de120,
            de121, de122, de123, de124, de125, de126, de127, de128, de129, de130,
            de131, de132, de133, de134, de135, de136, de137, de138, de139, de140,
            de141, de142, de143, de144, de145, de146, de147, de148, de149, de150,
            de151, de152, de153, de154, de155, de156, de157, de158, de159, de160,
            de161, de162, de163, de164, de165, de166, de167, de168, de169, de170,
            de171, de172, de173, de174, de175,
            resp_code_1, resp_desc_1, resp_code_2, resp_desc_2, 
            resp_code_4, resp_desc_4, resp_code_5, resp_desc_5,
            status_code, batch_id, mto_ref_no, remit_ident_detail, backend_status,
            br_settle_tmst, user_id, last_modified_by, last_modified_date,
            added_date, added_by, load_datetime
        FROM target.megalink_remit_trxn_hist_fct 
        WHERE de159 = %s
        LIMIT 1
        """
        
        try:
            connection.CLIENT.rollback()
            
            with connection.CLIENT.cursor() as cursor:
                cursor.execute(query, (get_remittance_transaction_request.de159,))
                result = cursor.fetchone()
                
                if not result:
                    return None

                columns = [desc[0] for desc in cursor.description]

                transaction_dict = {}
                for i, column in enumerate(columns):
                    value = result[i]
                    if value is None:
                        transaction_dict[column] = ""
                    else:
                        transaction_dict[column] = value
                
                return RemittanceTransaction(**transaction_dict)
                
        except Exception as e:
            print(f"Database query failed in RemittanceTransactionRepository: {str(e)}")
            try:
                connection.CLIENT.rollback()
            except:
                pass
            raise e