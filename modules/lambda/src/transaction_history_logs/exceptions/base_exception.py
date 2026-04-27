from __future__ import annotations


class CustomException(Exception):
    def __init__(
        self,
        custom_status_code: int | None = None,
        custom_error_code: str | None = None,
        custom_error_message: str | None = None,
        custom_error_details: str | None = None,
    ) -> None:
        if custom_status_code:
            self.STATUS_CODE = custom_status_code
        if custom_error_code:
            self.ERROR_CODE = custom_error_code
        if custom_error_message:
            self.ERROR_MESSAGE = custom_error_message
        if custom_error_details:
            self.ERROR_DETAILS = custom_error_details
        super().__init__(self.ERROR_MESSAGE)


class SuccessException(Exception):
    def __init__(
        self,
        exception_status_code: int | None = None,
        exception_success_code: str | None = None,
        exception_success_message: str | None = None,
        exception_details: str | None = None,
    ) -> None:
        if exception_status_code:
            self.STATUS_CODE = exception_status_code
        if exception_success_code:
            self.EXCEPTION_CODE = exception_success_code
        if exception_success_message:
            self.EXCEPTION_MESSAGE = exception_success_message
        if exception_details:
            self.EXCEPTION_DETAILS = exception_details
        super().__init__(self.EXCEPTION_MESSAGE)
