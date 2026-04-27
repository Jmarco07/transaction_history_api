import json
import os

import boto3
from botocore.exceptions import ClientError
from exceptions.secrets_manager_exceptions import SecretRetrievalException


class SecretRepository:
    CLIENT = boto3.client("secretsmanager", os.environ.get("AWS_REGION"))

    @classmethod
    def get_redshift_credentials(cls, secret_name):
        print("RETRIEVING CREDENTIALS FROM SECRETS MANAGER: ", secret_name)
        try:
            get_secret_value_response = cls.CLIENT.get_secret_value(
                SecretId=secret_name
            )

            secret_value = json.loads(get_secret_value_response["SecretString"])
            username = secret_value["username"]
            password = secret_value["password"]

            print("SUCCESSFULLY RETRIEVED REDSHIFT CREDENTIALS . . .")

            return {"username": username, "password": password}

        except ClientError as e:
            print(str(e))
            raise SecretRetrievalException
