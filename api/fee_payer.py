import json
from fastapi import APIRouter, Request
from libs import fee_payer

router = APIRouter()


@router.post('/feePayer/sign', response_model=fee_payer.SignedTransaction)
async def sign(request: Request):
    data = (await request.body()).decode('utf-8')
    with open('deserialized_transaction.txt', 'w') as f:
        f.write(data)
    signed_transaction = fee_payer.sign_transaction(data)
    return signed_transaction

