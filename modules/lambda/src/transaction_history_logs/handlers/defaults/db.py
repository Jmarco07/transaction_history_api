import os
import sys

import boto3
import psycopg2
from psycopg2.extensions import connection
from handlers.defaults.app import App
from repositories.secrets_repository import SecretRepository


def psycopg2_connect(app: App):
    """
    Connect to Redshift using psycopg2 with connection reuse.
    Only creates new connection if none exists or if existing connection is stale.
    """

    if app.CONNECTION is not None:
        try:
            with app.CONNECTION.CLIENT.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            print("Reusing existing healthy connection")
            return app.CONNECTION
        except (psycopg2.OperationalError, psycopg2.InterfaceError, AttributeError) as e:
            print(f"Existing connection is stale: {e}")
            try:
                app.CONNECTION.CLIENT.close()
            except:
                pass
            app.CONNECTION = None

    print("CONNECTING TO DATABASE . . .")
    
    try:
        credentials = SecretRepository.get_redshift_credentials(
            secret_name=os.getenv("REDSHIFT_SECRET_NAME")
        )

        db_connection = psycopg2.connect(
            dbname=os.getenv("REDSHIFT_DATABASE_NAME"),
            user=credentials["username"],
            password=credentials["password"],
            host=os.getenv("REDSHIFT_ENDPOINT"),
            port="5439",
            connect_timeout=30,
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5
        )

        with db_connection.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()

        class Psycopg2:
            CONNECTION_TYPE = "PSYCOPG2"
            CLIENT: connection = db_connection

        app.CONNECTION = Psycopg2
        app.CONNECTION_TYPE = "PSYCOPG2"

        print("SUCCESSFULLY CONNECTED!")
        return Psycopg2

    except Exception as e:
        print("ERROR: Could not connect to Database.")
        print(f"Error details: {str(e)}")

        app.CONNECTION = None
        app.CONNECTION_TYPE = None

        raise Exception(f"Database connection failed: {str(e)}")


def redshift_data_connect(app: App):
    """
    Connect to Redshift using Data API (serverless, no persistent connection).
    This is more Lambda-friendly as it doesn't maintain connections.
    """

    if app.CONNECTION is not None and app.CONNECTION_TYPE == "REDSHIFT_DATA":
        print("Reusing existing Data API client")
        return app.CONNECTION

    try:
        print("CONNECTING TO REDSHIFT DATA API . . .")

        class RedshiftDataBoto3:
            CONNECTION_TYPE = "REDSHIFT_DATA"
            CLIENT = boto3.client("redshift-data", region_name=os.environ.get("AWS_REGION"))
            DATABASE = os.getenv("REDSHIFT_DATABASE_NAME")
            SECRET_ARN = os.getenv("REDSHIFT_SECRET_ARN")
            WORKGROUP_NAME = os.getenv("REDSHIFT_WORKGROUP_NAME")

        app.CONNECTION = RedshiftDataBoto3
        app.CONNECTION_TYPE = RedshiftDataBoto3.CONNECTION_TYPE

        print("SUCCESSFULLY CONNECTED TO DATA API!")
        return RedshiftDataBoto3

    except Exception as e:
        print("ERROR: Could not connect to Redshift Data API.")
        print(f"Error details: {str(e)}")

        app.CONNECTION = None
        app.CONNECTION_TYPE = None

        raise Exception(f"Redshift Data API connection failed: {str(e)}")