from exceptions.base_exception import CustomException, SuccessException
from handlers.defaults.top_level import app
from utilities.base_response import (
    ErrorResponse,
    ExceptionResponse,
    SuccessExceptionResponse,
)


class BaseWrapper:
    def __init__(self, func):
        self.func = func
        self.func_name = func.__name__

    def __call__(self, *args, **kwargs):
        try:
            self.before_call(*args, **kwargs)
            result = self.func(*args, **kwargs)
            self.after_call(result, *args, **kwargs)
            response = result
        except CustomException as e:
            response = ErrorResponse(e)
        except SuccessException as e:
            response = SuccessExceptionResponse(e)
        except Exception as e:
            response = ExceptionResponse(e)
        finally:
            if app.CONNECTION is not None:
                if app.CONNECTION_TYPE == "PSYCOPG2":
                    pass
                    # commenting this part. We are keeping the connection active for scalability.
                    # idle connection timeout is handled in the database side
                    # print(f"CLOSING {app.CONNECTION_TYPE} CONNECTION . . .")
                    # app.CONNECTION.close()
                    # app.CONNECTION = None
                    # app.CONNECTION_TYPE = None
            return response

    def before_call(self, *args, **kwargs):
        """Code to execute before the function call"""
        pass

    def after_call(self, result, *args, **kwargs):
        """Code to execute after the function call"""
        pass


class CustomWrapper(BaseWrapper):
    def before_call(self, *args, **kwargs):
        print(f"START_EXECUTION: {self.func_name}")

    def after_call(self, result, *args, **kwargs):
        print(f"END_EXECUTION: {self.func_name}")


# @CustomWrapper
# def example_function(x, y):
#     return x + y

# result = example_function(2, 3)
# print(result)
