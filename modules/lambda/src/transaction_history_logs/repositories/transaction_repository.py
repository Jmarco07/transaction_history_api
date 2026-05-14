import base64
from typing import List, Tuple
from factories.sql_factory import SQLFactory
from models.requests.get_transactions import GetTransactionsRequest
from models.transaction_model import AgentTransaction


class TransactionRepository:
    MAX_LIMIT = 10000

    FIELD_COLUMN_MAP = {
        "agent": {
            "id": "merchant_id",
            "retRefNo": "retrrefno",
            "processedBy": "processedby",
            "serviceType": "servicetype",
            "traceNo": "traceno",
            "amount": "amount",
            "status": "statusdes",
            "transactionType": "trxntypeno",
        },
        "user": {
            "id": "walletId",
            "retRefNo": "retrrefno",
            "processedBy": "processedby",
            "serviceType": "servicetype",
            "traceNo": "traceno",
            "amount": "amount",
            "status": "statusdes",
            "transactionType": "trxntypeno",
        },
    }

    COLUMN_TYPE_MAP = {
        "id": "varchar",
        "retrrefno": "varchar",
        "processedby": "varchar",
        "servicetype": "varchar",
        "traceno": "varchar",
        "amount": "numeric",
        "statusdes": "varchar",
        "trxntypeno": "numeric",
    }

    COLUMN_MAPPING = {
        0: "trxnNo",
        1: "retRefNo",
        2: "cardNo",
        3: "source",
        4: "recipient",
        5: "amount",
        6: "trxnDate",
        7: "currency",
        8: "debitTrxn",
        9: "creditTrxn",
        10: "drCr",
        11: "description",
        12: "serviceType",
        13: "trxnTypeNo",
        14: "traceNo",
        15: "currencyCode",
        16: "merchant_id",
        17: "walletId",
        18: "senderName",
        19: "terminalId",
        20: "processedBy",
        21: "addedDate",
        22: "setlFlag",
        23: "statusDes",
        24: "insFlag",
    }

    @staticmethod
    def encode_cursor(trxn_no: str) -> str:
        return base64.b64encode(f"trxnno:{trxn_no}".encode()).decode()

    @staticmethod
    def decode_cursor(cursor: str) -> str:
        decoded = base64.b64decode(cursor.encode()).decode()
        return decoded.split(":", 1)[1]

    @classmethod
    def get(cls, connection, get_transactions_request: GetTransactionsRequest) -> Tuple[List, dict]:
        limit = min(get_transactions_request.limit or 1000, cls.MAX_LIMIT)

        adtl_filters = ""
        params = [
            f"{get_transactions_request.startDate} 00:00:00",
            f"{get_transactions_request.end_date} 23:59:59",
        ]

        def add_filter(field_name: str, values: list):
            nonlocal adtl_filters, params
            if not values:
                return

            column = cls.FIELD_COLUMN_MAP[get_transactions_request.type].get(field_name)
            if not column:
                print(f"⚠️ Skipping filter for '{field_name}' — no column mapping found")
                return

            col_type = cls.COLUMN_TYPE_MAP.get(column, "varchar")

            cleaned_values = []
            if col_type == "numeric":
                for v in values:
                    try:
                        cleaned_values = [str(v).strip() for v in values if str(v).strip()]
                    except (ValueError, TypeError):
                        print(f"Skipping invalid numeric value: {v}")
            else:
                cleaned_values = [str(v).strip() for v in values if v and str(v).strip()]

            if not cleaned_values:
                print(f"No valid values after cleaning for column '{column}'")
                return

            placeholders = ", ".join(["%s"] * len(cleaned_values))
            if col_type == "numeric":
                adtl_filters += f" AND {column} IN ({placeholders})"
            else:
                adtl_filters += f" AND TRIM({column}) IN ({placeholders})"
            params.extend(cleaned_values)

        add_filter("id", get_transactions_request.id)
        add_filter("retRefNo", get_transactions_request.retRefNo)
        add_filter("processedBy", get_transactions_request.processedBy)
        add_filter("serviceType", get_transactions_request.serviceType)
        add_filter("traceNo", get_transactions_request.traceNo)
        add_filter("amount", get_transactions_request.amount)
        add_filter("status", get_transactions_request.status)
        add_filter("transactionType", get_transactions_request.transactionType)

        cursor_filter = ""
        if get_transactions_request.cursor:
            cursor_value = cls.decode_cursor(get_transactions_request.cursor)
            if get_transactions_request.sort == "DESC":
                cursor_filter = " AND trxnno < %s"
            else:
                cursor_filter = " AND trxnno > %s"
            params.append(cursor_value)

        params.append(limit + 1)

        stmt = f"""
            SELECT 1;
            SELECT
                trxnno AS trxnNo,
                retrrefno AS retRefNo,
                cardno AS cardNo,
                sender AS source,
                receiver AS recipient,
                amount AS amount,
                trxndate AS trxnDate,
                currency AS currency,
                debittrxn AS debitTrxn,
                credittrxn AS creditTrxn,
                drcr AS drCr,
                description AS description,
                servicetype AS serviceType,
                trxntypeno AS trxnTypeNo,
                traceno AS traceNo,
                currencycode AS currencyCode,
                TRIM(merchantid) AS merchant_id,
                walletid AS walletId,
                sendername AS senderName,
                terminalid AS terminalId,
                processedby AS processedBy,
                addeddate AS addedDate,
                setlflag AS setlFlag,
                statusdes AS statusDes,
                insflag AS insFlag
            FROM target.mvw_megalink_agent_txn_history
            WHERE trxndate BETWEEN %s AND %s
                {adtl_filters}
                {cursor_filter}
            ORDER BY {get_transactions_request.orderBy} {get_transactions_request.sort}
            LIMIT %s;
        """

        print("\n==============================")
        print("Final query filters:", adtl_filters)
        print("Cursor filter:", cursor_filter)
        print("Final params:", params)
        print("==============================\n")

        results = list(SQLFactory(AgentTransaction).psycopg2_select(
            connection=connection,
            statement=stmt,
            params=params,
            column_mapping=cls.COLUMN_MAPPING,
        ) or [])

        has_next_page = len(results) > limit
        if has_next_page:
            results = results[:limit]

        has_previous_page = get_transactions_request.cursor is not None

        start_cursor = cls.encode_cursor(results[0].trxnNo) if results else None
        end_cursor = cls.encode_cursor(results[-1].trxnNo) if results else None

        page_info = {
            "hasNextPage": has_next_page,
            "hasPreviousPage": has_previous_page,
            "startCursor": start_cursor,
            "endCursor": end_cursor,
        }

        return results, page_info
