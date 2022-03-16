from datetime import datetime, timedelta
import os

import base58
import jwt
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from pydantic import BaseModel

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_401_UNAUTHORIZED

MESSAGE_TO_SIGN = """breakroom.show wants you to sign in with your Solana account:
{public_key_base58}


URI: https://breakroom.show/
Version: 1
Chain ID: 1
Nonce: {nonce}
Issued At: {issued_at}
"""

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/account/token")

_JWT_SIGNATURE_SECRET = os.environ['JWT_SIGNATURE_SECRET']
_JWT_TOKEN_TTL_DAYS = 30


class Credentials(BaseModel):
    id: str  # wallet public_key in base58


def _bytes_from_base58(base58_string: str) -> bytes:
    return base58.b58decode(base58_string)


def verify_signature(public_key_base58: str, nonce: str, issued_at: str, signature_base58: str) -> bool:
    public_key_bytes = _bytes_from_base58(public_key_base58)
    message = MESSAGE_TO_SIGN.format(
        public_key_base58=public_key_base58,
        nonce=nonce,
        issued_at=issued_at,
    )
    message_bytes = message.encode('utf-8')
    signature_bytes = _bytes_from_base58(signature_base58)
    verify_key = VerifyKey(public_key_bytes)
    try:
        verify_key.verify(message_bytes, signature_bytes)
    except BadSignatureError:
        return False
    return True


def issue_jwt_token(public_address_base58: str) -> str:
    encoded = jwt.encode(
        {'sub': public_address_base58, 'exp': datetime.utcnow() + timedelta(days=_JWT_TOKEN_TTL_DAYS)},
        _JWT_SIGNATURE_SECRET,
        algorithm="HS256"
    )
    return encoded


# FastAPI dependency
def get_credentials(jwt_token: str = Depends(oauth2_scheme)) -> Credentials:
    try:
        payload = jwt.decode(jwt_token, _JWT_SIGNATURE_SECRET, algorithms=["HS256"])
    except jwt.exceptions.PyJWTError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
        )
    public_address_base58 = payload['sub']
    return Credentials(
        id=public_address_base58
    )
