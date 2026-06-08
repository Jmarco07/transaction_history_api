import base64
import math
from typing import List, Tuple
from models.requests.get_pesonet_transaction import GetPesonetTransactionRequest
from models.pesonet_transaction_model import PesonetTransaction
from utilities.date_filter import to_start_of_day, to_end_of_day


class PesonetTransactionRepository:

    @staticmethod
    def encode_cursor(aux_no: str) -> str:
        return base64.b64encode(f"aux_no:{aux_no}".encode()).decode()

    @staticmethod
    def decode_cursor(cursor: str) -> str:
        decoded = base64.b64decode(cursor.encode()).decode()
        return decoded.split(":", 1)[1]

    @classmethod
    def _build_base_filters(cls, request: GetPesonetTransactionRequest):
        params = []
        filters = []

        if request.accountNumber:
            filters.append("TRIM(acc_id) = %s")
            params.append(request.accountNumber)

        if request.status:
            filters.append("TRIM(stat_desc) = %s")
            params.append(request.status)

        if request.fromDate and request.toDate:
            filters.append("CAST(add_date AS TIMESTAMP) BETWEEN CAST(%s AS TIMESTAMP) AND CAST(%s AS TIMESTAMP)")
            params.extend([to_start_of_day(request.fromDate), to_end_of_day(request.toDate)])
        elif request.fromDate:
            filters.append("CAST(add_date AS TIMESTAMP) >= CAST(%s AS TIMESTAMP)")
            params.append(to_start_of_day(request.fromDate))
        elif request.toDate:
            filters.append("CAST(add_date AS TIMESTAMP) <= CAST(%s AS TIMESTAMP)")
            params.append(to_end_of_day(request.toDate))

        return filters, params

    @classmethod
    def get_summary(cls, connection, request: GetPesonetTransactionRequest) -> dict:
        filters, params = cls._build_base_filters(request)
        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

        query = f"""
        SELECT
            COUNT(*) AS total_records,
            NVL(SUM(CASE WHEN msg_id = 'ibank_ft_pesonet' THEN CAST(trx_amt AS DECIMAL(18,2)) ELSE 0 END), 0) AS total_dr_amount,
            NVL(SUM(CASE WHEN msg_id = 'ibank_ft_pesonet_in' THEN CAST(trx_amt AS DECIMAL(18,2)) ELSE 0 END), 0) AS total_cr_amount,
            NVL(SUM(CASE WHEN TRIM(stat_desc) = 'Settled' THEN 1 ELSE 0 END), 0) AS total_settled,
            NVL(SUM(CASE WHEN TRIM(stat_desc) = 'Reversed' THEN 1 ELSE 0 END), 0) AS total_reversed
        FROM target.megalink_pesonet_trxn_hist_fct
        {where_clause}
        """

        try:
            with connection.CLIENT.cursor() as cursor:
                cursor.execute(query, tuple(params))
                row = cursor.fetchone()

                total_records = int(row[0]) if row else 0
                total_pages = math.ceil(total_records / request.limit) if total_records > 0 else 0

                return {
                    "totalRecords": total_records,
                    "totalPages": total_pages,
                    "totalDrAmount": float(row[1]) if row else 0,
                    "totalCrAmount": float(row[2]) if row else 0,
                    "totalSettled": int(row[3]) if row else 0,
                    "totalReversed": int(row[4]) if row else 0,
                }
        except Exception as e:
            print(f"Summary query failed: {str(e)}")
            try:
                connection.CLIENT.rollback()
            except:
                pass
            raise e

    @classmethod
    def get(cls, connection, request: GetPesonetTransactionRequest) -> Tuple[List[PesonetTransaction], dict]:
        filters, params = cls._build_base_filters(request)

        if request.cursor:
            cursor_value = cls.decode_cursor(request.cursor)
            filters.append("aux_no < %s")
            params.append(cursor_value)

        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

        params.append(request.limit + 1)

        query = f"""
        SELECT
            add_date, aux_no, trxn_reference_number, trxn_typ, trxn_type_desc,
            trx_amt, cur_id, acc_id, ext_rcvr_bnk_id, ext_rcvr_bnk_name,
            ext_acc_id, stat, resp_code, resp_desc, stat_desc,
            merchant_id, msg_id, load_datetime
        FROM target.megalink_pesonet_trxn_hist_fct
        {where_clause}
        ORDER BY aux_no DESC
        LIMIT %s
        """

        try:
            connection.CLIENT.rollback()

            with connection.CLIENT.cursor() as cursor:
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()

                if not rows:
                    page_info = {
                        "hasNextPage": False,
                        "hasPreviousPage": request.cursor is not None,
                        "startCursor": None,
                        "endCursor": None,
                    }
                    return [], page_info

                columns = [desc[0] for desc in cursor.description]

                results = []
                for row in rows:
                    transaction_dict = {}
                    for i, column in enumerate(columns):
                        value = row[i]
                        transaction_dict[column] = "" if value is None else value
                    results.append(PesonetTransaction(**transaction_dict))

                has_next_page = len(results) > request.limit
                if has_next_page:
                    results = results[:request.limit]

                has_previous_page = request.cursor is not None
                start_cursor = cls.encode_cursor(results[0].aux_no) if results else None
                end_cursor = cls.encode_cursor(results[-1].aux_no) if results else None

                page_info = {
                    "hasNextPage": has_next_page,
                    "hasPreviousPage": has_previous_page,
                    "startCursor": start_cursor,
                    "endCursor": end_cursor,
                }

                return results, page_info

        except Exception as e:
            print(f"Database query failed in PesonetTransactionRepository: {str(e)}")
            try:
                connection.CLIENT.rollback()
            except:
                pass
            raise e
