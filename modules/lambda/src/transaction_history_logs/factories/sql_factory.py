import time
from typing import Any, Generator, Literal
from pydantic import BaseModel

from exceptions.redshift_exceptions import (
    RedshiftAbortedQueryException,
    RedshiftActiveQueryException,
    RedshiftQueryException,
)


def SQLFactory(model: BaseModel):

    class SQL:
        @classmethod
        def psycopg2_select(
            cls, connection, statement: str, column_mapping: dict | None = None, params: tuple | None = None
        ) -> Generator[model, None, None] | None:
            print("SQLFactory: psycopg2_select: START")
            print("Statement:", statement.replace("\n", " "))

            with connection.CLIENT.cursor() as cur:
                try:
                    if params:
                        cur.execute(statement, params)
                    else:
                        cur.execute(statement)

                    rows = cur.fetchall()

                    if not column_mapping:
                        column_mapping = {i: desc.name for i, desc in enumerate(cur.description)}

                    if not rows:
                        print("SQLFactory: psycopg2_select: No rows returned.")
                        return []

                    data = cls._map_results(
                        results=rows,
                        column_mapping=column_mapping,
                        connection_type="PSYCOPG2",
                    )

                    print("SQLFactory: psycopg2_select: END")
                    return data

                except Exception as e:
                    print("SQLFactory: psycopg2_select: ERROR:", e)
                    try:
                        cur.execute("ROLLBACK")
                    except Exception:
                        pass
                    RedshiftQueryException.ERROR_DETAILS = str(e)
                    raise RedshiftQueryException

        @classmethod
        def redshift_data_execute_statement(cls, connection, statement: str) -> str:
            print("SQLFactory: redshift_data_execute_statement: START")
            print("Statement:", statement.replace("\n", " "))

            response = connection.CLIENT.execute_statement(
                Database=connection.DATABASE,
                SecretArn=connection.SECRET_ARN,
                Sql=statement,
                WorkgroupName=connection.WORKGROUP_NAME,
            )

            query_id = response.get("Id")
            print("EXECUTE_STATEMENT_RESPONSE:", response)
            print("STATEMENT_QUERY_ID:", query_id)
            return query_id

        @classmethod
        def redshift_data_get_statement_results(
            cls, connection, query_id: str, column_mapping: dict
        ) -> list[model]:
            print("SQLFactory: redshift_data_get_statement_results: START")

            total_iterations = 30
            iteration_count = 0
            sleep_interval = 0.5

            while True:
                statement = connection.CLIENT.describe_statement(Id=query_id)
                status = statement["Status"]
                print(f"Polling status [{iteration_count}/{total_iterations}]:", status)

                if status in ["FINISHED", "FAILED", "ABORTED"]:
                    break

                iteration_count += 1
                if iteration_count >= total_iterations:
                    print("Timeout waiting for Redshift statement to finish.")
                    raise RedshiftActiveQueryException

                time.sleep(sleep_interval)

            if status == "FAILED":
                error_msg = statement.get("Error", "Unknown error")
                print("Redshift statement FAILED:", error_msg)
                raise RedshiftQueryException(error_msg)

            if status == "ABORTED":
                print("Redshift statement ABORTED.")
                raise RedshiftAbortedQueryException

            print("FINAL_STATUS:", status)
            result = connection.CLIENT.get_statement_result(Id=query_id)

            records = result.get("Records", [])
            if not records:
                print("No records returned from Redshift Data API.")
                return []

            data = cls._map_results(
                results=records,
                column_mapping=column_mapping,
                connection_type="REDSHIFT_DATA",
            )

            print("SQLFactory: redshift_data_get_statement_results: END")
            return list(data)

        @staticmethod
        def _map_results(
            results,
            column_mapping: dict,
            connection_type: Literal["PSYCOPG2", "REDSHIFT_DATA"],
        ) -> Generator[Any, Any, None]:
            print("SQLFactory: _map_results: START")
            print("Column Mapping:", column_mapping)

            for row in results:
                processed_row = {}
                for idx, col_data in enumerate(row):
                    col_name = column_mapping.get(idx)

                    if connection_type == "PSYCOPG2":
                        processed_row[col_name] = col_data
                    elif connection_type == "REDSHIFT_DATA":
                        value = None
                        for key, val in col_data.items():
                            if key == "isNull" and val:
                                value = None
                            elif key != "isNull":
                                value = val
                        processed_row[col_name] = value

                yield model(**processed_row)

            print("SQLFactory: _map_results: END")

    SQL.model = model
    return SQL
