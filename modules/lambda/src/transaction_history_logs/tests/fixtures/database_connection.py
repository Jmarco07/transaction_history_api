import os

import psycopg2
import pytest
from dotenv import load_dotenv
from psycopg2.extensions import connection

load_dotenv()


@pytest.fixture
def redshift_connection():
    print("CONNECTING TO DATABASE . . .")
    conn: connection = psycopg2.connect(
        **{
            "dbname": os.getenv("redshift_dbname"),
            "user": os.getenv("redshift_user"),
            "password": os.getenv("redshift_password"),
            "host": os.getenv("redshift_host"),
            "port": os.getenv("redshift_port"),
        }
    )
    print("SUCCESSFULLY CONNECTED!")

    return conn
