""" scuba/libs/aws/testing.py

Test-only helpers for building AWS SNS payloads carrying a real signature
from a throwaway self-signed certificate, so tests exercise the actual
verification logic in scuba.libs.aws.sns instead of mocking it away.
"""
import base64
import datetime

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

from scuba.libs.aws.sns import _build_string_to_sign


def generate_test_keypair_and_cert():
    ''' returns (private_key, cert_pem_bytes) for a throwaway self-signed cert '''
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'sns-test')])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(now + datetime.timedelta(days=1))
        .sign(private_key, hashes.SHA256())
    )
    return private_key, cert.public_bytes(serialization.Encoding.PEM)


def sign_sns_payload(private_key, payload):
    ''' sets `payload["Signature"]` to a real signature over its canonical string, in place '''
    string_to_sign = _build_string_to_sign(payload)
    algorithm = hashes.SHA256() if str(payload.get('SignatureVersion', '1')) == '2' \
        else hashes.SHA1()
    signature_bytes = private_key.sign(
        string_to_sign.encode('utf-8'), padding.PKCS1v15(), algorithm)
    payload['Signature'] = base64.b64encode(signature_bytes).decode('ascii')
    return payload
