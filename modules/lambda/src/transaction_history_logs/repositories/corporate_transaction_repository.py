import base64
from typing import List, Tuple, Optional
from models.requests.get_corporate_transaction import GetCorporateTransactionRequest
from models.corporate_transaction_model import CorporateTransaction
from utilities.date_filter import to_start_of_day, to_end_of_day


class CorporateTransactionRepository:

    @staticmethod
    def encode_cursor(aux_no: str) -> str:
        return base64.b64encode(f"aux_no:{aux_no}".encode()).decode()

    @staticmethod
    def decode_cursor(cursor: str) -> str:
        decoded = base64.b64decode(cursor.encode()).decode()
        return decoded.split(":", 1)[1]

    @classmethod
    def get(cls, connection, request: GetCorporateTransactionRequest) -> Tuple[List[CorporateTransaction], dict]:
        params = []
        filters = []

        if request.accountNumber:
            filters.append("(TRIM(source_account) = %s OR TRIM(dest_account) = %s)")
            params.extend([request.accountNumber, request.accountNumber])

        if request.referenceNo:
            filters.append("TRIM(ret_ref_id) = %s")
            params.append(request.referenceNo)

        if request.transactionType:
            filters.append("TRIM(trx_type) = %s")
            params.append(request.transactionType)

        if request.merchantId:
            filters.append("TRIM(source) = %s")
            params.append(request.merchantId)

        if request.status:
            filters.append("TRIM(trx_stat) = %s")
            params.append(request.status)

        if request.fromDate and request.toDate:
            filters.append("CAST(trx_date AS TIMESTAMP) BETWEEN CAST(%s AS TIMESTAMP) AND CAST(%s AS TIMESTAMP)")
            params.extend([to_start_of_day(request.fromDate), to_end_of_day(request.toDate)])
        elif request.fromDate:
            filters.append("CAST(trx_date AS TIMESTAMP) >= CAST(%s AS TIMESTAMP)")
            params.append(to_start_of_day(request.fromDate))
        elif request.toDate:
            filters.append("CAST(trx_date AS TIMESTAMP) <= CAST(%s AS TIMESTAMP)")
            params.append(to_end_of_day(request.toDate))

        if request.postingType:
            filters.append("TRIM(c_d) = %s")
            params.append(request.postingType)

        if request.cursor:
            cursor_value = cls.decode_cursor(request.cursor)
            filters.append("aux_no < %s")
            params.append(cursor_value)

        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

        params.append(request.limit + 1)

        query = f"""
        SELECT
            c_d, trx_amt, trx_cur, trx_stat, trx_stat_desc,
            trx_date, trx_desc, trx_type, run_balance, ret_ref_id,
            aux_no, location, dest_account, total, contract_no,
            source, source_account, partner_ref_number, load_datetime
        FROM target.megalink_corporate_trxn_hist_fct
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
                    results.append(CorporateTransaction(**transaction_dict))

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
            print(f"Database query failed in CorporateTransactionRepository: {str(e)}")
            try:
                connection.CLIENT.rollback()
            except:
                pass
            raise e
