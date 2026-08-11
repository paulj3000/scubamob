"""
DynamoDB access for the chat domain (docs/chat_dynamo.md §11, §53).

A settings-driven table/client accessor, so the table name and region are
never scattered through the codebase (§11: "Do not scatter table names
throughout the code."). Message read/write logic lives in
MessageRepository's boto3-backed implementation (Phase 2); this module
only hands out configured session/table/client objects.
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


def get_client():
    """
    A plain low-level DynamoDB client, deliberately *not* table.meta.client
    -- a resource's .meta.client carries the resource layer's automatic
    type-transformation event handlers, which corrupt already-serialized
    AttributeValue items passed to low-level-only calls like
    transact_write_items (reproduced empirically: fails with a generic
    TransactionCanceledException/TypeError under moto). Raw calls that
    need manually-serialized items must use a client built straight from
    the session instead.
    """
    return get_session().client('dynamodb')
