import os
import sys

import boto3
import psycopg2
from handlers.defaults.app import App
from psycopg2.extensions import connection
from repositories.secrets_repository import SecretRepository


def psycopg2_connect(app: App):

    class Psycopg2:
        CONNECTION_TYPE = "PSYCOPG2"
        CREDENTIALS = SecretRepository.get_redshift_credentials(  # make sure secrets manager endpoint is setup and aligned with the vpcs
            secret_name=os.getenv("REDSHIFT_SECRET_NAME")
        )
        CLIENT: connection = psycopg2.connect(
            **{
                "dbname": os.getenv("REDSHIFT_DATABASE_NAME"),
                "user": CREDENTIALS["username"],
                "password": CREDENTIALS["password"],
                "host": os.getenv("REDSHIFT_ENDPOINT"),
                "port": "5439",
            }
        )

    try:
        if app.CONNECTION is None:

            print("CONNECTING TO DATABASE . . .")
            app.CONNECTION = psycopg2.connect(...)
            app.CONNECTION_TYPE = "PSYCOPG2"

            print("SUCCESSFULLY CONNECTED!")

            return Psycopg2

    except Exception as e:
        print("ERROR: Unexpected error: Could not connect to Database.")
        print(str(e))

        app.CONNECTION = None
        app.CONNECTION_TYPE = None
        sys.exit()


def redshift_data_connect(app: App):

    class RedshiftDataBoto3:
        CONNECTION_TYPE = "REDSHIFT_DATA"
        CLIENT = boto3.client("redshift-data", os.environ.get("AWS_REGION"))
        DATABASE = os.getenv("REDSHIFT_DATABASE_NAME")
        SECRET_ARN = os.getenv("REDSHIFT_SECRET_NAME")
        WORKGROUP_NAME = os.getenv("REDSHIFT_WORKGROUP_NAME")

    try:
        print("CONNECTING TO DATABASE . . .")
        app.CONNECTION = RedshiftDataBoto3
        app.CONNECTION_TYPE = RedshiftDataBoto3.CONNECTION_TYPE
        print("SUCCESSFULLY CONNECTED!")

        return RedshiftDataBoto3

    except Exception as e:
        print("ERROR: Unexpected error: Could not connect to Database.")
        print(str(e))

        app.CONNECTION = None
        app.CONNECTION_TYPE = None
        sys.exit()
