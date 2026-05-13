from typing import Optional
from models.requests.get_qr_emvco_transaction import GetQrEmvcoTransactionRequest
from models.qr_emvco_transaction_model import QrEmvcoTransaction


class QrEmvcoTransactionRepository:

    @staticmethod
    def get(connection, get_qr_emvco_transaction_request: GetQrEmvcoTransactionRequest) -> Optional[QrEmvcoTransaction]:
        query = """
        SELECT
            id, pfi, pim, mid, qr_code_data, mcc, curr_code, amt,
            convnc_ind, convnc_fee, convnc_per, cntry_code, merc_name, merc_city,
            pstl_code, adtnl_bill_data, bill_num, mobile_num, store_lbl, loylty_num,
            ref_lbl, cust_lbl, trmnl_lbl, purpose, adtnl_consumr_data, merc_lang,
            merc_lang_data, bnk_code, merc_bnk, sub_acq, pymt_typ,
            optnl_1, optnl_2, optnl_3, optnl_4, optnl_5, optnl_6, optnl_7,
            optnl_8, optnl_9, optnl_10, optnl_11, optnl_12, optnl_13, optnl_14,
            optnl_15, optnl_16, optnl_17, optnl_18, optnl_19, optnl_20, optnl_21,
            optnl_22, optnl_23, optnl_24, optnl_25, optnl_26, optnl_27, optnl_28,
            optnl_29, optnl_30, optnl_31, optnl_32, optnl_33, optnl_34, optnl_35,
            stat, mrchnt_id, tid, ntwrk, tx_origin, tx_stat,
            adt_merc_name, adt_merc_city, tx_typ, crc, exp_time,
            d_map, res_d_map, call_bak_url, ntfy_enbl, ref_id, ret_ref_id,
            add_by, add_date, mdfy_by, mdfy_date, load_datetime
        FROM target.megalink_qr_code_emvco_hist_fct
        WHERE optnl_16 = %s
        LIMIT 1
        """

        try:
            connection.CLIENT.rollback()

            with connection.CLIENT.cursor() as cursor:
                cursor.execute(query, (get_qr_emvco_transaction_request.optnl_16,))
                result = cursor.fetchone()

                if not result:
                    return None

                columns = [desc[0] for desc in cursor.description]

                transaction_dict = {}
                for i, column in enumerate(columns):
                    value = result[i]
                    transaction_dict[column] = "" if value is None else value

                return QrEmvcoTransaction(**transaction_dict)

        except Exception as e:
            print(f"Database query failed in QrEmvcoTransactionRepository: {str(e)}")
            try:
                connection.CLIENT.rollback()
            except:
                pass
            raise e
