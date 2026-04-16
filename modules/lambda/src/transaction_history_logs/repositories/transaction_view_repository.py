from typing import Optional, List, Dict
from factories.sql_factory import SQLFactory
from models.transaction_view_model import TransactionView
from decimal import Decimal
from datetime import datetime

class TransactionViewRepository(SQLFactory(TransactionView)):

    @classmethod
    def get_transaction_view(cls, connection, ret_ref_id: str) -> Optional[dict]:
        """
        Fetch transaction details for the view endpoint.
        Parse custom_fld into label/value pairs (supports label-only segments).
        Returns all columns including parsed custom fields.
        """
        escaped_ret_ref_id = ret_ref_id.replace("'", "''")

        stmt = f"""
            SELECT
                retr_ref_no AS trxn_no,
                added_date::timestamp AS added_date,
                trxn_typ_nature AS service_type,
                trace_no AS traceId,
                transaction_type AS trxnType,
                trxn_typ_description AS description,
                cr_dr AS cardType,
                rspn_code AS responseCode,
                rspn_status AS status,
                billing_amount AS amount,
                gate_variant AS gateVariant,
                COALESCE(CAST(custom_fld AS varchar), '') AS custom_fld
            FROM target.megalink_transaction_gl_hist_fct
            WHERE retr_ref_no = '{escaped_ret_ref_id}'
            ORDER BY added_date DESC
            LIMIT 1;
        """

        column_mapping = {
            0: "trxn_no",
            1: "added_date",
            2: "service_type",
            3: "traceId",
            4: "type",
            5: "description",
            6: "cardType",
            7: "responseCode",
            8: "status",
            9: "amount",
            10: "gateVariant",
            11: "custom_fld"
        }

        results = list(
            super(TransactionViewRepository, cls).psycopg2_select(
                connection=connection,
                statement=stmt,
                column_mapping=column_mapping,
            )
        )

        if not results:
            return None

        result = results[0]
        if hasattr(result, "model_dump"):
            result = result.model_dump()

        result["type"] = result.pop("trxnType", None)

        result["amount"] = Decimal(result.get("amount") or 0)
        result["responseCode"] = (
            int(result.get("responseCode")) if result.get("responseCode") is not None else 0
        )

        raw_custom = result.get("custom_fld") or ""
        custom_fields: List[Dict[str, str]] = []

        for segment in raw_custom.split("|"):
            segment = segment.strip()
            if not segment:
                continue
            if "~" in segment:
                label, value = segment.split("~", 1)
            else:
                label, value = segment, ""
            custom_fields.append({"label": label.strip(), "value": value.strip()})

        result["fields"] = custom_fields

        for key in ["trxn_no", "added_date", "service_type", "cardType", "gateVariant", "custom_fld", "traceId", "description", "status"]:
            if key not in result:
                result[key] = None

        if isinstance(result.get("added_date"), str):
            try:
                result["added_date"] = datetime.fromisoformat(result["added_date"])
            except ValueError:
                result["added_date"] = None

        return result
