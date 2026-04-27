import pytest


@pytest.fixture
def unvalidated_body():
    return {
        "cardNumber": "0000050066080249442946",
        "id": "123123123",
        "lastTrxnNo": "328714131784",
        "limit": "2",
        "range": "10",
        "startDate": "2024-07-01",
        "type": "user",
    }
