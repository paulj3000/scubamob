"""
DynamoDB access for the chat domain (docs/chat_dynamo.md §11, §53).

Phase 0 scope only: a settings-driven table accessor, so the table name
and region are never scattered through the codebase (§11: "Do not scatter
table names throughout the code."). No message read/write logic lives
here yet -- that's MessageRepository's boto3-backed implementation,
Phase 2. Nothing in this module is called by anything yet, so importing
it never triggers a real AWS call; tests mock boto3 directly rather than
hitting DynamoDB Local (Phase 0 doesn't wire that up -- CLAUDE.md forbids
tests depending on live external services, and chat.repositories'
InMemoryMessageRepository fake already covers local dev/test needs).
"""
import os

import boto3

from scuba.settings import AWS_PROFILE, CHAT_DYNAMODB_REGION, CHAT_DYNAMODB_TABLE


def get_session():
    """ Same credential resolution as scuba.libs.aws.s3.S3.get_session(). """
    if os.getenv('AWS_SECRET_ACCESS_KEY') and os.getenv('AWS_ACCESS_KEY_ID'):
        return boto3.Session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=CHAT_DYNAMODB_REGION,
        )
    return boto3.Session(profile_name=AWS_PROFILE, region_name=CHAT_DYNAMODB_REGION)


def get_table(table_name: str = CHAT_DYNAMODB_TABLE):
    """ The boto3 Table resource for the chat messages table. """
    session = get_session()
    return session.resource('dynamodb').Table(table_name)
