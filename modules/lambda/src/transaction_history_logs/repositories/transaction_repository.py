from typing import List
from factories.sql_factory import SQLFactory
from models.requests.get_transactions import GetTransactionsRequest
from models.transaction_model import AgentTransaction, CorporateTransaction


class TransactionRepository:
    MAX_LIMIT = 5000

    FIELD_COLUMN_MAP = {
        "agent": {
            "retRefNo": "retrrefno",
            "processedBy": "processedby",
            "serviceType": "servicetype",
            "traceNo": "traceno",
            "amount": "amount",
            "status": "statusdes",
            "transactionType": "trxntypeno",
        },
        "corporate": {
            "retRefNo": "trxn_reference_number",
            "amount": "trxn_amt",
            "status": "upload_status",
            "transactionType": "trxn_typ",
        },
    }

    COLUMN_TYPE_MAP = {
        "retrrefno": "varchar",
        "processedby": "varchar",
        "servicetype": "varchar",
        "traceno": "varchar",
        "amount": "numeric",
        "statusdes": "varchar",
        "trxntypeno": "numeric",
        "trxn_reference_number": "varchar",
        "trxn_amt": "numeric",
        "upload_status": "varchar",
        "trxn_typ": "numeric",
    }

    @classmethod
    def get(cls, connection, get_transactions_request: GetTransactionsRequest) -> List:
        limit = min(get_transactions_request.limit or 1000, cls.MAX_LIMIT)
        offset = (get_transactions_request.offset - 1) * limit

        adtl_filters = ""
        params = [
            f"{get_transactions_request.startDate} 00:00:00",
            f"{get_transactions_request.end_date} 23:59:59",
        ]

        def add_filter(field_name: str, values: list):
            """Dynamically build IN clause for varchar or numeric fields."""
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
                        cleaned_values.append(float(v))
                    except (ValueError, TypeError):
                        print(f"   ❌ Skipping invalid numeric value: {v}")
            else:
                cleaned_values = [str(v).strip() for v in values if v and str(v).strip()]


            if not cleaned_values:
                print(f"⚠️ No valid values after cleaning for column '{column}'")
                return

            placeholders = ", ".join(["%s"] * len(cleaned_values))
            adtl_filters += f" AND {column} IN ({placeholders})"
            params.extend(cleaned_values)

            print(f"   • Added to filters: {adtl_filters}")
            print(f"   • Current params  : {params}")

        if get_transactions_request.type == "agent":
            add_filter("retRefNo", get_transactions_request.retRefNo)
            add_filter("processedBy", get_transactions_request.processedBy)
            add_filter("serviceType", get_transactions_request.serviceType)
            add_filter("traceNo", get_transactions_request.traceNo)
            add_filter("amount", get_transactions_request.amount)
            add_filter("status", get_transactions_request.status)
            add_filter("transactionType", get_transactions_request.transactionType)

            params.extend([limit, offset])

            stmt = f"""
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
                    merchantid AS merchant_id,
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
                ORDER BY {get_transactions_request.orderBy} {get_transactions_request.sort}
                LIMIT %s OFFSET %s;
            """

            print("\n==============================")
            print("🔍 Final query filters:", adtl_filters)
            print("🔸 Final params:", params)
            print("==============================\n")

            return SQLFactory(AgentTransaction).psycopg2_select(
                connection=connection,
                statement=stmt,
                params=params,
                column_mapping={
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
                },
            )

        elif get_transactions_request.type == "corporate":
            add_filter("retRefNo", get_transactions_request.retRefNo)
            add_filter("amount", get_transactions_request.amount)
            add_filter("status", get_transactions_request.status)
            add_filter("transactionType", get_transactions_request.transactionType)

            params.extend([limit, offset])

            stmt = f"""
                SELECT
                    filename AS fileName,
                    uploaded_by AS uploadedBy,
                    uploaded_date AS uploadedDate,
                    account_id AS acctNo,
                    bulk_id AS bulkId,
                    aux_no AS auxNo,
                    claim_code AS claimCode,
                    from_account AS fromAcct,
                    to_account AS toAcct,
                    trxn_amt AS trxnAmount,
                    trxn_type_desc AS trxnDesc,
                    receiver_first_name AS firstName,
                    receiver_middle_name AS middleName,
                    receiver_last_name AS lastName,
                    receiver_mobile_no AS mobileNo,
                    optional_1 AS optional1,
                    optional_2 AS optional2,
                    optional_3 AS optional3,
                    optional_4 AS optional4,
                    optional_5 AS optional5,
                    optional_6 AS optional6,
                    optional_7 AS optional7,
                    optional_8 AS optional8,
                    optional_9 AS optional9,
                    optional_10 AS optional10,
                    optional_11 AS optional11,
                    optional_12 AS optional12,
                    resp_code AS respCode,
                    upload_status AS uploadStat,
                    trxn_reference_number AS trxnRefNo,
                    trxn_typ AS transactionType
                FROM target.mv_megalink_bulk_pepp_disbursement_90d
                WHERE CAST(uploaded_date AS TIMESTAMP) BETWEEN %s AND %s
                    {adtl_filters}
                ORDER BY {get_transactions_request.orderBy} {get_transactions_request.sort}
                LIMIT %s OFFSET %s;
            """

            return SQLFactory(CorporateTransaction).psycopg2_select(
                connection=connection,
                statement=stmt,
                params=params,
                column_mapping={
                    0: "fileName",
                    1: "uploadedBy",
                    2: "uploadedDate",
                    3: "acctNo",
                    4: "bulkId",
                    5: "auxNo",
                    6: "claimCode",
                    7: "fromAcct",
                    8: "toAcct",
                    9: "trxnAmount",
                    10: "trxnDesc",
                    11: "firstName",
                    12: "middleName",
                    13: "lastName",
                    14: "mobileNo",
                    15: "optional1",
                    16: "optional2",
                    17: "optional3",
                    18: "optional4",
                    19: "optional5",
                    20: "optional6",
                    21: "optional7",
                    22: "optional8",
                    23: "optional9",
                    24: "optional10",
                    25: "optional11",
                    26: "optional12",
                    27: "respCode",
                    28: "uploadStat",
                    29: "trxnRefNo",
                    30: "transactionType",
                },
            )

        return []
