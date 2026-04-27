from models.requests.get_transactions import GetTransactionsRequest
from pydantic_core._pydantic_core import ValidationError
from tests.fixtures.get_transaction_request import unvalidated_body


def missing_field_function(unvalidated_body, field):
    try:
        unvalidated_body_copy = unvalidated_body.copy()
        del unvalidated_body_copy[field]
        get_transaction_request = GetTransactionsRequest(**unvalidated_body_copy)

        assert isinstance(get_transaction_request, GetTransactionsRequest)
        error_type = None
        error_field = None
    except ValidationError as exc:
        error_type = exc.errors()[0]["type"]
        error_field = exc.errors()[0]["loc"][0]
        assert error_type == "missing"
        assert error_field == field


def test_get_transaction_request(unvalidated_body):
    get_transaction_request = GetTransactionsRequest(**unvalidated_body)
    assert isinstance(get_transaction_request, GetTransactionsRequest)


def test_get_transaction_request_with_missing_cardNumber(unvalidated_body):
    missing_field_function(unvalidated_body, "cardNumber")


def test_get_transaction_request_with_missing_id(unvalidated_body):
    missing_field_function(unvalidated_body, "id")


def test_get_transaction_request_with_missing_lastTrxnNo(unvalidated_body):
    missing_field_function(unvalidated_body, "lastTrxnNo")


def test_get_transaction_request_with_missing_limit(unvalidated_body):
    missing_field_function(unvalidated_body, "limit")


def test_get_transaction_request_with_missing_range(unvalidated_body):
    missing_field_function(unvalidated_body, "range")


def test_get_transaction_request_with_missing_startDate(unvalidated_body):
    missing_field_function(unvalidated_body, "startDate")


def test_get_transaction_request_with_missing_type(unvalidated_body):
    missing_field_function(unvalidated_body, "type")
