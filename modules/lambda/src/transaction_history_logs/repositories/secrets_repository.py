import json
import os

import boto3
from botocore.exceptions import ClientError
from exceptions.secrets_manager_exceptions import SecretRetrievalException


class SecretRepository:
    CLIENT = boto3.client("secretsmanager", os.environ.get("AWS_REGION"))
    _cached_credentials = None

    @classmethod
    def get_redshift_credentials(cls, secret_name):
        if cls._cached_credentials is not None:
            print("REUSING CACHED REDSHIFT CREDENTIALS")
            return cls._cached_credentials

        print("RETRIEVING CREDENTIALS FROM SECRETS MANAGER: ", secret_name)
        try:
            get_secret_value_response = cls.CLIENT.get_secret_value(
                SecretId=secret_name
            )

            secret_value = json.loads(get_secret_value_response["SecretString"])
            cls._cached_credentials = {
                "username": secret_value["username"],
                "password": secret_value["password"],
            }

            print("SUCCESSFULLY RETRIEVED REDSHIFT CREDENTIALS . . .")
            return cls._cached_credentials

        except ClientError as e:
            print(str(e))
            raise SecretRetrievalException
