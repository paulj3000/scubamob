"""
# scuba/libs/aws/sns.py

Verifies the authenticity of inbound AWS SNS webhook messages by validating
their signature against the certificate AWS publishes at SigningCertURL, per
https://docs.aws.amazon.com/sns/latest/dg/sns-verify-signature-of-message.html
"""
import base64
import re
from urllib.parse import urlparse

import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509 import load_pem_x509_certificate

# AWS only ever serves signing certificates from an "sns.<region>.amazonaws.com" host.
# Restricting to that pattern (over https) stops an attacker from pointing SigningCertURL
# at a server they control and self-signing their own "valid" message.
SIGNING_CERT_HOST_RE = re.compile(r'^sns\.[a-z0-9-]+\.amazonaws\.com$', re.IGNORECASE)

NOTIFICATION_FIELDS = ('Message', 'MessageId', 'Subject', 'Timestamp', 'TopicArn', 'Type')
CONFIRMATION_FIELDS = (
    'Message', 'MessageId', 'SubscribeURL', 'Timestamp', 'Token', 'TopicArn', 'Type')

REQUEST_TIMEOUT_SECONDS = 5


class SNSVerificationError(Exception):
    ''' raised when an inbound SNS message fails signature verification '''


def _canonical_fields(message_type):
    if message_type in ('SubscriptionConfirmation', 'UnsubscribeConfirmation'):
        return CONFIRMATION_FIELDS
    return NOTIFICATION_FIELDS


def _build_string_to_sign(payload):
    fields = _canonical_fields(payload.get('Type'))
    lines = []
    for field in fields:
        if field not in payload:
            # Subject is the one optional field in a Notification message.
            if field == 'Subject':
                continue
            raise SNSVerificationError(f'SNS message is missing required field "{field}".')
        lines.append(field)
        lines.append(str(payload[field]))
    return '\n'.join(lines) + '\n'


def _fetch_certificate(signing_cert_url):
    parsed = urlparse(signing_cert_url)
    if parsed.scheme != 'https' or not SIGNING_CERT_HOST_RE.match(parsed.hostname or ''):
        raise SNSVerificationError(
            f'SigningCertURL host "{parsed.hostname}" is not a trusted AWS SNS host.')

    try:
        response = requests.get(signing_cert_url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise SNSVerificationError(f'Could not fetch SigningCertURL: {exc}') from exc

    return response.content


def verify_signature(payload):
    ''' raise SNSVerificationError unless `payload` carries a valid AWS SNS signature '''
    signing_cert_url = payload.get('SigningCertURL')
    signature = payload.get('Signature')
    signature_version = str(payload.get('SignatureVersion', '1'))

    if not signing_cert_url or not signature:
        raise SNSVerificationError('SNS message is missing SigningCertURL or Signature.')

    string_to_sign = _build_string_to_sign(payload)
    cert_bytes = _fetch_certificate(signing_cert_url)

    try:
        certificate = load_pem_x509_certificate(cert_bytes)
        signature_bytes = base64.b64decode(signature)
    except Exception as exc:
        raise SNSVerificationError(
            f'Could not parse SNS certificate or signature: {exc}') from exc

    algorithm = hashes.SHA256() if signature_version == '2' else hashes.SHA1()

    try:
        certificate.public_key().verify(
            signature_bytes, string_to_sign.encode('utf-8'), padding.PKCS1v15(), algorithm)
    except InvalidSignature as exc:
        raise SNSVerificationError('SNS message signature is invalid.') from exc
