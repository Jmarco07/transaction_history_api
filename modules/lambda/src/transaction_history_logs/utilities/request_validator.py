from __future__ import annotations

import json
from typing import Any, Type

from exceptions.model_exceptions import PydanticBaseModelException
from exceptions.request_exceptions import (
    RequestValidationException,
    BadRequestException
)
from handlers.defaults.top_level import app
from pydantic import BaseModel, ValidationError
from utilities.function_wrapper import BaseWrapper

class RequestValidator(BaseWrapper):
    def __init__(self, func, model):
        super().__init__(func)
        self.model = model

    def before_call(self, *args, **kwargs):
        event = args[0]
        context = args[1]
        validate(event, self.model)
        print(f"START_EXECUTION: {self.func_name}")

    def after_call(self, result, *args, **kwargs):
        print(f"END_EXECUTION: {self.func_name}")


def request_validator(model):
    def decorator(func):
        return RequestValidator(func, model)

    return decorator


def validate(event, model):
    if not issubclass(model, BaseModel):  # type: ignore
        raise PydanticBaseModelException
    
    print("REQUEST", event)
    body: dict[Any, Any] = {}
    if event["body"]:
        try:
            body = json.loads(event["body"])
        except (json.JSONDecodeError, TypeError):
            raise BadRequestException(
                custom_error_details="Invalid or malformed JSON in request body"
            )
    if event["queryStringParameters"]:
        body = {**body, **event["queryStringParameters"]}
    if event["pathParameters"]:
        body = {**body, **event["pathParameters"]}

    # Check for required 'limit' field on list endpoints
    if "limit" in {f.alias or name for name, f in model.model_fields.items()}:
        if "limit" not in body or body["limit"] is None or body["limit"] == "":
            raise BadRequestException(
                custom_error_details="limit is required"
            )

    print("UNVALIDATED_BODY", body)
    result = _validate_data(body, model_class=model, context={"body": body})

    if not isinstance(result, BaseModel):
        RequestValidationException.ERROR_DETAILS = _construct_validation_error_message(
            result
        )
        raise RequestValidationException

    app.VALIDATED_BODY = result
    

def _validate_data(
    data: dict[str, Any], model_class: Type[BaseModel], context: dict[str, Any]
) -> BaseModel | dict[Any, Any]:
    try:
        validated_data = model_class.model_validate(data, context=context)
        return validated_data
    except ValidationError as e:
        errors: dict[Any, Any] = {}
        for error in e.errors():
            loc = error.get("loc", ())
            field_name = loc[0] if loc else "date"
            msg = error["msg"]
            if msg.startswith("Value error, "):
                msg = msg[len("Value error, "):]
            errors[field_name] = msg

        print("VALIDATION_ERRORS: ", errors)
        return errors


def _construct_validation_error_message(
    validated_data: dict[Any, Any]
) -> list[dict[str, Any]]:
    error_message_list: list[dict[Any, Any]] = []
    for field, error in validated_data.items():
        temp_dict: dict[Any, Any] = {}
        temp_dict["field"] = field
        temp_dict["error"] = error
        error_message_list.append(temp_dict)

    return error_message_list
