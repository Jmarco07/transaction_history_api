import base64
import math
from typing import List, Tuple, Optional
from models.requests.get_bulk_pepp_disbursement import GetBulkPeppDisbursementRequest
from models.bulk_pepp_disbursement_model import BulkPeppDisbursementTransaction
from utilities.date_filter import to_start_of_day, to_end_of_day


class BulkPeppDisbursementRepository:
    MAX_LIMIT = 10000

    COLUMN_MAPPING = {
        0: "company_id",
        1: "filename",
        2: "uploaded_by",
        3: "uploaded_date",
        4: "account_id",
        5: "bulk_id",
        6: "msg_id",
        7: "aux_no",
        8: "claim_code",
        9: "from_account",
        10: "to_account",
        11: "trxn_amt",
        12: "trxn_typ",
        13: "trxn_type_desc",
        14: "receiver_first_name",
        15: "receiver_middle_name",
        16: "receiver_last_name",
        17: "receiver_mobile_no",
        18: "stat_code",
        19: "itrl_usr_msg_code",
        20: "usr_msg_code",
        21: "optional_1",
        22: "optional_2",
        23: "optional_3",
        24: "optional_4",
        25: "optional_5",
        26: "optional_6",
        27: "optional_7",
        28: "optional_8",
        29: "optional_9",
        30: "optional_10",
        31: "optional_11",
        32: "optional_12",
        33: "resp_code",
        34: "upload_status",
        35: "trxn_status",
        36: "trxn_reference_number",
        37: "last_modified_by",
        38: "last_modified_date",
        39: "load_datetime",
    }

    @staticmethod
    def encode_cursor(value: str) -> str:
        return base64.b64encode(f"trxnno:{value}".encode()).decode()

    @staticmethod
    def decode_cursor(cursor: str) -> str:
        decoded = base64.b64decode(cursor.encode()).decode()
        return decoded.split(":", 1)[1]

    @classmethod
    def _build_status_filter(cls, status_values: List[str]) -> str:
        """Build custom status filter based on status codes"""
        filters = []
        for status in status_values:
            if status == "0":
                filters.append("resp_code IN ('00', '000')")
            elif status == "1":
                filters.append("(UPPER(usr_msg_code) = 'INVALID ACCOUNT' OR UPPER(trxn_status) = 'INVALID ACCOUNT')")
            elif status == "2":
                filters.append("(itrl_usr_msg_code = '7415' OR itrl_usr_msg_code = '7416')")
            elif status == "3":
                filters.append("(UPPER(usr_msg_code) = 'INSUFFICIENT BALANCE' OR UPPER(trxn_status) = 'INSUFFICIENT BALANCE')")
            elif status == "4":
                filters.append("(msg_id = 'rmt_send' AND stat_code = '18')")
            elif status == "5":
                filters.append("(msg_id = 'rmt_send' AND stat_code = '11')")
            elif status == "6":
                filters.append("itrl_usr_msg_code = 'ACTY_00_10'")
            else:
                raise ValueError(f"No matching status found: {status}")

        if filters:
            return " AND (" + " OR ".join(filters) + ")"
        return ""

    @classmethod
    def _build_base_filters(cls, request: GetBulkPeppDisbursementRequest):
        params = []
        filters = " WHERE 1=1"

        if request.accountNumbers:
            placeholders = ", ".join(["%s"] * len(request.accountNumbers))
            filters += f" AND from_account IN ({placeholders})"
            params.extend(request.accountNumbers)

        if request.fileId:
            placeholders = ", ".join(["%s"] * len(request.fileId))
            filters += f" AND bulk_id IN ({placeholders})"
            params.extend(request.fileId)

        if request.transactionTypes:
            placeholders = ", ".join(["%s"] * len(request.transactionTypes))
            filters += f" AND msg_id IN ({placeholders})"
            params.extend(request.transactionTypes)

        if request.fromDate:
            filters += " AND CAST(uploaded_date AS TIMESTAMP) >= CAST(%s AS TIMESTAMP)"
            params.append(to_start_of_day(request.fromDate))

        if request.toDate:
            filters += " AND CAST(uploaded_date AS TIMESTAMP) <= CAST(%s AS TIMESTAMP)"
            params.append(to_end_of_day(request.toDate))

        if request.status:
            status_filter = cls._build_status_filter(request.status)
            filters += status_filter

        return filters, params

    @classmethod
    def get_summary(cls, connection, request: GetBulkPeppDisbursementRequest) -> dict:
        filters, params = cls._build_base_filters(request)

        query = f"""
        SELECT
            COUNT(*) AS total_records,
            NVL(SUM(CAST(trxn_amt AS DECIMAL(18,2))), 0) AS total_amount,
            COUNT(CASE
                WHEN msg_id IN ('ibank_ft', 'ibank_ft_intl') AND resp_code IN ('00', '000') THEN 1
                WHEN msg_id = 'rmt_send' AND resp_code IN ('00', '000') AND trxn_status IN ('UNCLAIMED', 'CLAIMED', 'CANCELLED') THEN 1
                ELSE NULL END) AS total_success,
            COUNT(CASE
                WHEN msg_id IN ('ibank_ft', 'ibank_ft_intl') AND (resp_code IS NULL OR resp_code NOT IN ('00', '000')) THEN 1
                WHEN msg_id = 'rmt_send' AND resp_code IS NOT NULL AND resp_code NOT IN ('00', '000') THEN 1
                ELSE NULL END) AS total_failed,
            COUNT(CASE WHEN msg_id = 'rmt_send' AND trxn_status = 'CLAIMED' THEN 1 ELSE NULL END) AS total_claimed_pepp,
            COUNT(CASE WHEN msg_id = 'rmt_send' AND trxn_status = 'UNCLAIMED' THEN 1 ELSE NULL END) AS total_unclaimed_pepp
        FROM target.megalink_bulk_pepp_disbursement_hist_fct
        {filters}
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
                    "totalAmount": float(row[1]) if row else 0,
                    "totalSuccess": int(row[2]) if row else 0,
                    "totalFailed": int(row[3]) if row else 0,
                    "totalClaimedPepp": int(row[4]) if row else 0,
                    "totalUnclaimedPepp": int(row[5]) if row else 0,
                }
        except Exception as e:
            print(f"Summary query failed: {str(e)}")
            try:
                connection.CLIENT.rollback()
            except:
                pass
            raise e

    @classmethod
    def get(cls, connection, get_bulk_pepp_disbursement_request: GetBulkPeppDisbursementRequest) -> Tuple[List[BulkPeppDisbursementTransaction], dict]:
        limit = min(get_bulk_pepp_disbursement_request.limit, cls.MAX_LIMIT)
        filters, params = cls._build_base_filters(get_bulk_pepp_disbursement_request)

        # Cursor-based pagination
        cursor_filter = ""
        if get_bulk_pepp_disbursement_request.cursor:
            cursor_value = cls.decode_cursor(get_bulk_pepp_disbursement_request.cursor)
            cursor_filter = " AND trxn_reference_number < %s"
            params.append(cursor_value)

        # Add limit + 1 to check for next page
        params.append(limit + 1)

        query = f"""
            SELECT 1;
            SELECT
                company_id, filename, uploaded_by, uploaded_date, account_id,
                bulk_id, msg_id, aux_no, claim_code, from_account,
                to_account, trxn_amt, trxn_typ, trxn_type_desc,
                receiver_first_name, receiver_middle_name, receiver_last_name, receiver_mobile_no,
                stat_code, itrl_usr_msg_code, usr_msg_code,
                optional_1, optional_2, optional_3, optional_4, optional_5,
                optional_6, optional_7, optional_8, optional_9, optional_10,
                optional_11, optional_12,
                resp_code, upload_status, trxn_status, trxn_reference_number,
                last_modified_by, last_modified_date, load_datetime
            FROM target.megalink_bulk_pepp_disbursement_hist_fct
            {filters}
            {cursor_filter}
            ORDER BY uploaded_date DESC
            LIMIT %s;
        """

        print("\n==============================")
        print("Final query filters:", filters)
        print("Cursor filter:", cursor_filter)
        print("Final params:", params)
        print("==============================\n")

        try:
            connection.CLIENT.rollback()

            with connection.CLIENT.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()

                if not rows:
                    return [], {
                        "hasNextPage": False,
                        "hasPreviousPage": get_bulk_pepp_disbursement_request.cursor is not None,
                        "startCursor": None,
                        "endCursor": None,
                    }

                results = []
                for row in rows:
                    transaction_dict = {}
                    for idx, value in enumerate(row):
                        col_name = cls.COLUMN_MAPPING.get(idx)
                        if col_name:
                            transaction_dict[col_name] = value if value is not None else ""
                    results.append(BulkPeppDisbursementTransaction(**transaction_dict))

                has_next_page = len(results) > limit
                if has_next_page:
                    results = results[:limit]

                has_previous_page = get_bulk_pepp_disbursement_request.cursor is not None

                start_cursor = cls.encode_cursor(results[0].trxn_reference_number) if results else None
                end_cursor = cls.encode_cursor(results[-1].trxn_reference_number) if results else None

                page_info = {
                    "hasNextPage": has_next_page,
                    "hasPreviousPage": has_previous_page,
                    "startCursor": start_cursor,
                    "endCursor": end_cursor,
                }

                return results, page_info

        except Exception as e:
            print(f"Database query failed in BulkPeppDisbursementRepository: {str(e)}")
            try:
                connection.CLIENT.rollback()
            except:
                pass
            raise e
