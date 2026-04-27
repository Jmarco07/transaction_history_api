import jwt
import boto3
import os
from botocore.exceptions import ClientError


def generate_policy(principal_id, effect, route_arn):
    """Helper function to generate the IAM policy document"""

    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "execute-api:Invoke",
                "Effect": effect,
                "Resource": route_arn,
            }
        ],
    }

    return {"principalId": principal_id, "policyDocument": policy_document}


def get_cauth_details(sub, aud):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.getenv("CAUTH_TOKENS_DDB"))

    try:
        response = table.get_item(
            Key={
                "sub": sub,
                "aud": aud,
            }
        )
        return response
    except ClientError as e:
        print(f"Error getting item: {e.response['Error']['Message']}")
        raise Exception(f"DynamoDB Error: {e.response['Error']['Message']}")


def lambda_handler(event, context):
    identity_source = event.get("identitySource")
    route_arn = event.get("routeArn")

    print("event", event)

    try:
        if not identity_source:
            raise Exception("Unauthorized Token [CV-1]")

        authorization = identity_source[0]

        if not authorization.startswith("Bearer "):
            raise Exception("Unauthorized Token [CV-2]")

        token = authorization[len("Bearer ") :]

        decoded_token = jwt.decode(token, options={"verify_signature": False})

        sub = decoded_token.get("sub", None)
        aud = decoded_token.get("aud", None)

        if not sub or not aud:
            raise Exception("Unauthorized Token [CV-3]")

        cauth = get_cauth_details(sub, aud)

        if "Item" not in cauth:
            raise Exception("Unauthorized Token [CV-4]")

        cauth_details = cauth.get("Item")

        jwt.decode(
            token,
            cauth_details["secret"],
            algorithms=["HS256"],
            audience=cauth_details["aud"],
        )

        return generate_policy(aud, "Allow", route_arn)

    except Exception as e:
        print("UNAUTHORIZED_EXCEPTION: ", e)
        return generate_policy("unknown_user", "Deny", route_arn)
