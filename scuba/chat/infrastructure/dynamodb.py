"""
DynamoDB access for the chat domain (docs/chat_dynamo.md §11, §53).

A settings-driven table accessor, so the table name and region are never
scattered through the codebase (§11: "Do not scatter table names
throughout the code."). Message read/write logic itself lives in
scuba.chat.repositories.message_repository.DynamoDBMessageRepository
(Phase 2), which calls get_table() rather than talking to boto3 directly.
Importing this module never triggers a real AWS call; tests mock
get_table()/boto3 directly rather than hitting DynamoDB Local (CLAUDE.md
forbids tests depending on live external services, and
InMemoryMessageRepository covers local dev/test needs in the meantime).
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
