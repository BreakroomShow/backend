from starlette.status import HTTP_400_BAD_REQUEST
from fastapi import APIRouter, HTTPException, Depends
from libs import auth, redis_connection
from models import used_nonce

router = APIRouter()


@router.post('/account/token')
def login(
        public_key_base58: str,
        nonce: str,
        issued_at_string: str,
        signature_base58: str,
        redis_conn: redis_connection.Redis = Depends(redis_connection.get_redis_connection)
):
    if not auth.verify_signature(
        public_key_base58=public_key_base58,
        nonce=nonce,
        issued_at=issued_at_string,
        signature_base58=signature_base58
    ):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Bad message signature.",
        )

    if used_nonce.exists(redis_conn, nonce):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Bad nonce.",
        )
    used_nonce.save(redis_conn, nonce)

    return {'token': auth.issue_jwt_token(public_key_base58)}


@router.get('/account/messageToSign')
def get_login_message(
        public_key_base58: str,
        nonce: str,
        issued_at_string: str,
):
    return auth.MESSAGE_TO_SIGN.format(
        public_key_base58=public_key_base58,
        nonce=nonce,
        issued_at=issued_at_string,
    )
