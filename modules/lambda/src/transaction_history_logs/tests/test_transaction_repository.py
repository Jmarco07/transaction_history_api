from models.requests.get_transactions import GetTransactionsRequest
from repositories.transaction_repository import Transaction, TransactionRepository
from tests.fixtures.database_connection import redshift_connection
from tests.fixtures.get_transaction_request import unvalidated_body


class TestTransactionRepository:
    def test_get(self, unvalidated_body, redshift_connection):
        try:
            transactions: list[Transaction] = TransactionRepository.get(
                connection=redshift_connection,
                get_transactions_request=GetTransactionsRequest(**unvalidated_body),
            )
        except Exception as e:
            print(f"ERROR: Unexpected error: {str(e)}")
            transactions = None
        finally:
            assert type(transactions) == list
            assert isinstance(transactions[0], Transaction)
