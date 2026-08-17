"""
S3 access for chat attachments (docs/chat_dynamo.md §5, §30, Phase 11).

A settings-driven client accessor, mirroring infrastructure/dynamodb.py's
get_client() -- so CHAT_ATTACHMENT_BUCKET is the only place the bucket
name is configured. Upload/presigned-URL logic lives in AttachmentStorage's
boto3-backed implementation (scuba.chat.repositories.attachment_repository.
S3AttachmentStorage); this module only hands out a configured client.
"""
import os

import boto3
from botocore.client import Config

from scuba.settings import AWS_PROFILE, CHAT_ATTACHMENT_BUCKET

# SigV4 explicitly -- some regions (anything launched after January 2014)
# reject the legacy SigV2 signing boto3 can still fall back to for a
# client with no region configured, and presigned URLs must be valid
# wherever CHAT_ATTACHMENT_BUCKET actually lives.
_CLIENT_CONFIG = Config(signature_version='s3v4')


def get_session():
    """ Same credential resolution as scuba.chat.infrastructure.dynamodb.get_session(). """
    if os.getenv('AWS_SECRET_ACCESS_KEY') and os.getenv('AWS_ACCESS_KEY_ID'):
        return boto3.Session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        )
    return boto3.Session(profile_name=AWS_PROFILE)


def get_client():
    """
    A low-level S3 client -- generate_presigned_url is a client-only
    method (§30: "Use signed URLs when private content is retrieved."),
    so one client covers both puts and presigning.
    """
    return get_session().client('s3', config=_CLIENT_CONFIG)


def get_bucket_name() -> str:
    return CHAT_ATTACHMENT_BUCKET
