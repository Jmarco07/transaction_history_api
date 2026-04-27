from typing import Optional
from decimal import Decimal

from factories.sql_factory import SQLFactory
from models.transaction_view_model import TransactionView


class TransactionViewRepository(SQLFactory(TransactionView)):

    @classmethod
    def get_transaction_view(cls, connection, ret_ref_id: str) -> Optional[dict]:
        stmt = """
            SELECT
                retr_ref_no AS trxnNo,
                trc_no AS traceId,
                biller_category AS billerCategory,
                biller AS biller,
                bill_date::timestamp AS billDate,
                account_number AS acctNo,
                account_name AS acctName,
                date::timestamp AS date,
                processed_by AS processedBy,
                amount,
                convenience_fee AS convenienceFee,
                total_amount AS totalAmount,
                trace_status AS traceStatus,
                description AS desc,
                sender_mobile_no AS sndrMobileNo,
                receiver_account_no AS rcvrAcctNo
            FROM target.megalink_transaction_hist
            WHERE retr_ref_no = %s
            ORDER BY date DESC
            LIMIT 1;
        """

        column_mapping = {
            0: "trxnNo",
            1: "traceId",
            2: "billerCategory",
            3: "biller",
            4: "billDate",
            5: "acctNo",
            6: "acctName",
            7: "date",
            8: "processedBy",
            9: "amount",
            10: "convenienceFee",
            11: "totalAmount",
            12: "traceStatus",
            13: "desc",
            14: "sndrMobileNo",
            15: "rcvrAcctNo",
        }

        results = list(
            super().psycopg2_select(
                connection=connection,
                statement=stmt,
                column_mapping=column_mapping,
                params=(ret_ref_id,),
            )
        )

        if not results:
            return None

        result = results[0]

        if hasattr(result, "model_dump"):
            result = result.model_dump()

        for field in ["amount", "convenienceFee", "totalAmount"]:
            value = result.get(field)
            if isinstance(value, Decimal):
                result[field] = str(value)
            elif value is None:
                result[field] = "0"
            else:
                result[field] = str(value)

        return result
