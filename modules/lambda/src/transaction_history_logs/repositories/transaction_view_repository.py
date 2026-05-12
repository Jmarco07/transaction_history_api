from typing import Optional
from datetime import datetime

from factories.sql_factory import SQLFactory
from models.transaction_view_model import TransactionView


class TransactionViewRepository(SQLFactory(TransactionView)):

    @classmethod
    def get_transaction_view(cls, connection, ret_ref_id: str) -> Optional[dict]:
        stmt = """
            SELECT 1;
            SELECT
                retr_ref_no AS trxnNo,
                trxn_typ_nature AS trxnTypeNature,
                trxn_typ_description AS trxnTypeDescription,
                amount,
                converted_amount AS convertedAmount,
                fees,
                receiver_country AS receiverCountry,
                remittance_partner AS remittancePartner,
                delivery_method AS deliveryMethod,
                location AS location,
                pin,
                item,
                txn_datetime::timestamp AS date,
                pawn_ticket_no AS pawnTicketNo,
                bulk_ref_no AS bulkRefNo,
                trace_no AS traceNo,
                order_no AS orderNo,
                biller AS biller,
                product,
                fee,
                sender_from AS senderFrom,
                discount,
                total_amount AS totalAmount,
                merchant,
                provider,
                sku,
                account_number AS acctNo,
                acct_no_mobile_no AS acctNoMobileNo,
                recipient,
                recipient_name AS recipientName,
                claim_code AS claimCode,
                recipient_no AS recipientNo,
                partner,
                protektodo_package AS protektodoPackage,
                policy_holder AS policyHolder,
                to_account AS toAccount,
                loyalty_no AS loyaltyNo,
                source,
                receiver,
                account,
                purpose,
                sender,
                sender_account_name AS senderAccountName,
                status,
                ref_card_id AS refCardId,
                transaction_id AS transactionId,
                token,
                bank
            FROM target.transaction_history_api
            WHERE retr_ref_no = %s
            ORDER BY date DESC
            LIMIT 1;
        """

        column_mapping = {
            0: "trxnNo",
            1: "trxnTypeNature",
            2: "trxnTypeDescription",
            3: "amount",
            4: "convertedAmount",
            5: "fees",
            6: "receiverCountry",
            7: "remittancePartner",
            8: "deliveryMethod",
            9: "location",
            10: "pin",
            11: "item",
            12: "date",
            13: "pawnTicketNo",
            14: "bulkRefNo",
            15: "traceNo",
            16: "orderNo",
            17: "biller",
            18: "product",
            19: "fee",
            20: "senderFrom",
            21: "discount",
            22: "totalAmount",
            23: "merchant",
            24: "provider",
            25: "sku",
            26: "acctNo",
            27: "acctNoMobileNo",
            28: "recipient",
            29: "recipientName",
            30: "claimCode",
            31: "recipientNo",
            32: "partner",
            33: "protektodoPackage",
            34: "policyHolder",
            35: "toAccount",
            36: "loyaltyNo",
            37: "source",
            38: "receiver",
            39: "account",
            40: "purpose",
            41: "sender",
            42: "senderAccountName",
            43: "status",
            44: "refCardId",
            45: "transactionId",
            46: "token",
            47: "bank",
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

        if result.get("date") and isinstance(result["date"], datetime):
            result["date"] = result["date"].strftime("%m/%d/%Y %I:%M %p")

        for key, value in result.items():
            if value is None:
                result[key] = ""

        return result
