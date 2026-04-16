import random
import string
import jwt
import datetime
import boto3
import os
import json
from botocore.exceptions import ClientError


def generate_secret(length=16):
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(characters) for _ in range(length))


def generate_jwt_token(sub, aud, secret):
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    exp_utc = now_utc + datetime.timedelta(days=365)

    payload = {
        "sub": sub,
        "aud": aud,
        "iat": int(now_utc.timestamp()),
        "exp": int(exp_utc.timestamp()),
    }

    return jwt.encode(payload, secret, algorithm="HS256")


def put_item(item):
    table_name = os.getenv("CAUTH_TOKENS_DDB")
    if not table_name:
        raise Exception("Environment variable CAUTH_TOKENS_DDB not set")

    table = boto3.resource("dynamodb").Table(table_name)
    table.put_item(Item=item)


def lambda_handler(event, context=None):
    body = event.get("body")
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Invalid JSON body."}),
                "headers": {"Content-Type": "application/json"}
            }

    sub = body.get("sub", "") if body else ""
    aud = body.get("aud", "") if body else ""
    description = body.get("description", "") if body else ""

    if sub not in ["agent", "corporate"]:
        return {
            "statusCode": 422,
            "body": json.dumps({"message": "Invalid sub value ['agent', 'corporate']."}),
            "headers": {"Content-Type": "application/json"}
        }
    if not aud:
        return {
            "statusCode": 422,
            "body": json.dumps({"message": "aud value is required."}),
            "headers": {"Content-Type": "application/json"}
        }
    if not description:
        return {
            "statusCode": 422,
            "body": json.dumps({"message": "description value is required."}),
            "headers": {"Content-Type": "application/json"}
        }

    try:
        secret = generate_secret()
        token = generate_jwt_token(sub, aud, secret)

        decoded = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={"verify_exp": False, "verify_aud": False}  # ✅ disable audience validation
        )

        put_item({
            "sub": sub,
            "aud": aud,
            "secret": secret,
            "token": token,
            "description": description,
            "iat": decoded["iat"],
            "exp": decoded["exp"],
        })

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Token Generated Successfully",
                "token": token,
                "expires_at": datetime.datetime.utcfromtimestamp(decoded["exp"]).isoformat() + "Z"
            }),
            "headers": {"Content-Type": "application/json"}
        }

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": f"Error generating token: {str(e)}"}),
            "headers": {"Content-Type": "application/json"}
        }
