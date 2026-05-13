from typing import Optional
from models.requests.get_ibank_ft_transaction import GetIbankFtTransactionRequest
from models.ibank_ft_transaction_model import IbankFtTransaction


class IbankFtTransactionRepository:

    @staticmethod
    def get(connection, get_ibank_ft_transaction_request: GetIbankFtTransactionRequest) -> Optional[IbankFtTransaction]:
        query = """
        SELECT
            msg_id, aux_no, sndr, chal_valdt, msg_grp_id, card_no,
            fr_acc_id, fr_acc_lbl, to_acc_id, to_acc_lbl,
            org_bnk_cod, dest_bnk_cod, dell, org_brch_cod, dest_brch_cod,
            trx_amt, cur_id, chnl_typ, narrat, originating_acc_holder_name,
            trxn_code, stat, co_id, schd_id, bulk_id, tnx_type,
            network_type, acc_cur, converted_amt, is_foreign,
            resp_code, resp_desc,
            receiver_first_name, receiver_middle_name, receiver_last_name,
            receiver_mobile_no, purpose,
            optional_1, optional_2, optional_3, optional_4, optional_5,
            optional_6, optional_7, optional_8, optional_9, optional_10,
            optional_11, optional_12, optional_13, optional_14, optional_15,
            sender_nationality, claimcode, sender_first_name, sender_last_name,
            sender_mobile_number, sender_address, ret_ref_id, receiver_address,
            ext_batch_id, ext_rcvr_bnk_id, ext_rcvr_bnk_name,
            ext_trx_stat, ext_trx_desc, orig_trxn_no,
            last_modified_by, last_modified_date, load_datetime
        FROM target.megalink_ibank_ft_trxn_hist_fct
        WHERE msg_id = %s AND ret_ref_id = %s
        LIMIT 1
        """

        try:
            connection.CLIENT.rollback()

            with connection.CLIENT.cursor() as cursor:
                cursor.execute(query, (
                    get_ibank_ft_transaction_request.msg_id,
                    get_ibank_ft_transaction_request.ret_ref_id,
                ))
                result = cursor.fetchone()

                if not result:
                    return None

                columns = [desc[0] for desc in cursor.description]

                transaction_dict = {}
                for i, column in enumerate(columns):
                    value = result[i]
                    transaction_dict[column] = "" if value is None else value

                return IbankFtTransaction(**transaction_dict)

        except Exception as e:
            print(f"Database query failed in IbankFtTransactionRepository: {str(e)}")
            try:
                connection.CLIENT.rollback()
            except:
                pass
            raise e
