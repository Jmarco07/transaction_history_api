from decimal import Decimal
from typing import Generator

from exceptions.redshift_exceptions import RedshiftConnectionException
from factories.sql_factory import SQLFactory
from models.requests.get_transactions import GetTransactionsRequest
from models.transaction_model import Transaction


class TransactionRepository(SQLFactory(Transaction)):

    @classmethod
    def get(
        cls,
        connection,
        get_transactions_request: GetTransactionsRequest,
    ) -> Generator[Transaction, None, None] | None:
        stmt = f"""
            SELECT
                tl.trxn_no as trxnNo,
                CAST(te.trxn_no AS VARCHAR) as retrRefNo,
                CAST(ta.card_no_hash AS VARCHAR) as cardNo,
                ta.origin_bank_code as source,
                CAST(ta.dest_account_no AS VARCHAR) as recepient,
                te.trxn_amount as amount,
                te.trxn_date as trxnDate,
                te.trxn_currency_code as currency,
                te.debit_trxn as debitTrxn,
                te.credit_trxn as creditTrxn,
                te.drcr as drCr,
                te.trxn_type as description,
                te.service_type as serviceType,
                te.trxn_type_no as trxnTypeNo,
                CAST(ta.trace_no AS VARCHAR) as traceNo,
                ta.trxn_currency_code as currencyCode,
                ta.merchant_id as merchant_id,
                ta.wallet_id as walletId,
                ta.sndr_nme as senderName,
                tl.term_id as terminalId,
                tl.added_by as processedBy,
                tl.added_date as addedDate,
                tl.setl_flag as setlFlag,
                tl.stat_desc as statusDes,
                tl.insurance_flag as insFlag
            FROM target.megalink_transactions_enriched te 
            LEFT OUTER JOIN target.megalink_transaction_all_hist_fct ta
                ON te.trxn_no = ta.retr_ref_no
            LEFT OUTER JOIN target.megalink_transaction_log_hist_fct tl
                ON te.trxn_no = tl.retr_ref_no 
                AND te.trxn_type_no = tl.trxn_typ
            WHERE te.trxn_date BETWEEN '{get_transactions_request.startDate} 00:00:00'
                                  AND '{get_transactions_request.end_date} 23:59:59'
            ORDER BY te.trxn_date {get_transactions_request.sort}
            LIMIT {get_transactions_request.limit} 
            OFFSET ({get_transactions_request.offset} - 1) * {get_transactions_request.limit};
        """

        results = super(cls, cls).psycopg2_select(
            connection=connection,
            statement=stmt,
            column_mapping={
                0: "trxnNo",
                1: "retRefNo",
                2: "cardNo",
                3: "source",         # sender
                4: "recipient",      # receiver
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

        return results
