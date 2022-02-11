import os
from typing import List, Dict
import base58
from pydantic import BaseModel
from solana.transaction import Transaction
from solana.message import CompiledInstruction
from solana.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Confirmed
from libs import authority_solana


class SourceMessage(BaseModel):
    header: Dict[str, int]
    account_keys: List[str]
    recent_blockhash: str
    instructions: List[CompiledInstruction]


class SignedTransaction(BaseModel):
    source_message: SourceMessage
    signature_base58: str


def sign_transaction(raw_transaction_base58: str) -> SignedTransaction:
    transaction_bytes = base58.b58decode(raw_transaction_base58)
    transaction = Transaction.deserialize(transaction_bytes)
    # transaction.add_signer(_fee_payer_keypair())
    compiled_message = transaction.compile_message()
    # compiled_message.header = MessageHeader(
    #     num_required_signatures=2,
    #     num_readonly_signed_accounts=1,
    #     num_readonly_unsigned_accounts=2,
    # )
    print(compiled_message.instructions)
    signature = base58.b58encode(_fee_payer_keypair().sign(compiled_message.serialize()).signature).decode('utf-8')
    return SignedTransaction(
        source_message=SourceMessage(
            header=compiled_message.header._asdict(),
            account_keys=[public_key.to_base58() for public_key in compiled_message.account_keys],
            recent_blockhash=compiled_message.recent_blockhash,
            instructions=compiled_message.instructions,
        ),
        signature_base58=signature,
    )


# FIXME
# Debug code:
#
async def update_transaction():
    client = AsyncClient("https://api.devnet.solana.com")

    with open('deserialized_transaction.txt') as f:
        transaction_bytes = base58.b58decode(f.read())
    transaction = Transaction.deserialize(transaction_bytes)

    print(transaction.signatures)
    #print(transaction.serialize())

    transaction.add_signer(_fee_payer_keypair())
    #transaction.fee_payer = _fee_payer_keypair().public_key

    print(transaction.signatures)

    print('[signature]', [int(b) for b in transaction.signatures[1].signature])
    print('[header]', transaction.compile_message().header, )
    print('[account_keys]', transaction.compile_message().account_keys)
    print('[recent_blockhash]', transaction.compile_message().recent_blockhash)
    print('[instructions]', transaction.compile_message().instructions)
    print('[serialize]', [int(b) for b in transaction.compile_message().serialize()])
    print('[signed message]', [
        int(b)
        for b in authority_solana._authority_wallet().payer.sign(transaction.compile_message().serialize()).signature
    ])
    value = bytearray(transaction.compile_message().serialize())
    value[1] = 1
    print('[signed message 2]', [
        int(b)
        for b in authority_solana._authority_wallet().payer.sign(bytes(value)).signature
    ])

    transaction.signatures[1].signature = None
    #transaction.add_signer(authority_solana._authority_wallet().payer)

    print('[signature]', [int(b) for b in transaction.signatures[1].signature])

    # print(transaction.serialize())

    await client.simulate_transaction(transaction)
    result = await client.send_raw_transaction(transaction.serialize(), opts=TxOpts(preflight_commitment=Confirmed))

    return result


def _fee_payer_keypair():
    return Keypair.from_secret_key(base58.b58decode(os.environ['FEE_PAYER_PRIVATE_KEY_BASE58']))
