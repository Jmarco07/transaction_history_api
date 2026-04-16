# from typing import Any, Generator

# from handlers.defaults.db import redshift_data_connect
# from handlers.defaults.top_level import app
# from models.requests.get_transactions import GetTransactionsRequest
# from models.responses.get_transactions import GetTransactionsResponse
# from repositories.transaction_repository import Transaction, TransactionRepository
# from utilities.base_response import SuccessResponse
# from utilities.request_validator import request_validator

# redshift_data_connect(app)


# @request_validator(model=GetTransactionsRequest)
# def lambda_handler(event, context) -> dict[str, Any]:
#     print("app CONNECTION STATE: ", app.CONNECTION)

#     transactions: Generator[Transaction, None, None] | list = TransactionRepository.get(
#         connection=app.CONNECTION, get_transactions_request=app.VALIDATED_BODY
#     )

#     last_transaction_no = None
#     deduplicated_transactions = []

#     if transactions:
#         deduplicated_transactions: list[Transaction] = (
#             TransactionRepository.combine_principal_and_fees(transactions)
#         )

#         last_transaction_no = deduplicated_transactions[-1].retrRefNo

#     response = {
#         "result": {
#             "total": len(deduplicated_transactions),
#             "data": deduplicated_transactions,
#         },
#         "lastTrxnNo": last_transaction_no,
#     }

#     return SuccessResponse(**GetTransactionsResponse(**response).model_dump())
