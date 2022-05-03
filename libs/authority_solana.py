import asyncio
import time
import json
import hashlib
from pathlib import Path
import os
from typing import Tuple, List, Optional
from datetime import datetime
import base58
from pydantic import BaseModel
from solana.rpc.async_api import AsyncClient
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.system_program import SYS_PROGRAM_ID
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Confirmed, Finalized
from solana.rpc.core import RPCException
from solana.sysvar import SYSVAR_RENT_PUBKEY
from solana.exceptions import SolanaRpcException
from anchorpy import Program, Provider, Wallet, Idl, Context
from anchorpy.utils.token import create_mint_and_vault
from spl.token.constants import TOKEN_PROGRAM_ID

_DEVNET_DEPLOYED_PROGRAM_ID = "Eb7ZLJqhTDmLDcoGbKUy6DKxSBraNEsfbDST4FWiXAwv"

TRIVIA = b'trivia'
GAME = b'game'
USER = b'user'
PLAYER = b'player'
VAULT = b'vault'
VAULT_AUTHORITY = b'vault_authority'


def _message_from_rpc_error(error: RPCException) -> Optional[str]:
    if len(error.args) == 1 and type(error.args[0]) == dict:
        return error.args[0].get('message')


class AccountsNotFound(Exception):
    pass


class PrizeFund(BaseModel):
    amount: int
    mint: PublicKey
    deposit_account: PublicKey

    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True


async def main():
    client = AsyncClient("https://api.devnet.solana.com")
    provider = Provider(client, _authority_wallet(), TxOpts())
    program_id = PublicKey("Eb7ZLJqhTDmLDcoGbKUy6DKxSBraNEsfbDST4FWiXAwv")
    program = Program(_idl(), program_id, provider)
    pda, bump = _trivia_pda(program_id)

    await program.rpc["initialize"](bump, ctx=Context(accounts={
        'trivia': pda,
        'authority': provider.wallet.public_key,
        'system_program': SYS_PROGRAM_ID
    }, signers=[provider.wallet.payer]))

    await program.close()


async def get_program(official_rpc=False) -> Program:
    rpc_url = 'https://wispy-summer-river.solana-devnet.quiknode.pro/a4030f5defc3f7b7306d2460e35578282d1fe8b8/'
    if official_rpc:
        rpc_url = 'https://api.devnet.solana.com'
    client = AsyncClient(rpc_url)
    # TxOpts(skip_preflight=True) to skip simulation
    provider = Provider(client, _authority_wallet(), TxOpts())
    program_id = PublicKey(_DEVNET_DEPLOYED_PROGRAM_ID)
    program = Program(_idl(), program_id, provider)

    return program


async def wait_until_accounts_created(program: Program, accounts: List[PublicKey], limit_seconds: int = 60):
    print('[wait_until_accounts_created]', 'started')
    started = time.time()
    while (time.time() - started) < limit_seconds:
        try:
            accounts_values = (await program.provider.connection.get_multiple_accounts(accounts, Finalized))['result']['value']
        except SolanaRpcException as e:
            print('[wait_until_accounts_created]', 'exception', e)
            await asyncio.sleep(0.5)
            continue
        print(accounts_values)
        if all([value is not None for value in accounts_values]):
            print('[wait_until_accounts_created]', 'finished')
            return True
        await asyncio.sleep(0.5)
    raise AccountsNotFound()


async def create_devnet_prize_fund(program: Program, owner: PublicKey) -> PrizeFund:
    amount = 100

    retries = 3
    for retry in range(retries):
        try:
            (mint_public_key, vault_public_key) = await create_mint_and_vault(program.provider, amount, owner)
            break
        except RPCException as error:
            error_message = _message_from_rpc_error(error)
            is_last_retry = retry == (retries - 1)
            should_retry = error_message == 'Transaction simulation failed: Blockhash not found'
            if should_retry and not is_last_retry:
                continue
            raise error

    await wait_until_accounts_created(program, [mint_public_key, vault_public_key])
    return PrizeFund(
        amount=amount,
        mint=mint_public_key,
        deposit_account=vault_public_key
    )


async def create_game(program: Program, name: str, start_time: datetime, prize_fund: PrizeFund) -> int:
    trivia_pda, trivia_bump = _trivia_pda(program.program_id)
    games_counter = (await program.account['Trivia'].fetch(trivia_pda)).games_counter

    game_pda, _ = _game_pda(program.program_id, trivia_pda, games_counter)
    vault_pda, _ = _vault_pda(program.program_id, game_pda)
    vault_authority_pda, _ = _vault_authority_pda(program.program_id, game_pda)

    print(prize_fund.mint)

    options = program.type['GameOptions'](name=name, start_time=int(start_time.timestamp()), prize_fund_amount=prize_fund.amount)

    retries = 3
    for retry in range(retries):
        try:
            result = await program.rpc["create_game"](options, ctx=Context(accounts={
                'game': game_pda,
                'trivia': trivia_pda,
                'authority': program.provider.wallet.public_key,
                'prize_fund_mint': prize_fund.mint,
                'prize_fund_vault': vault_pda,
                'prize_fund_deposit': prize_fund.deposit_account,
                'prize_fund_vault_authority': vault_authority_pda,
                'system_program': SYS_PROGRAM_ID,
                'token_program': TOKEN_PROGRAM_ID,
                'rent': SYSVAR_RENT_PUBKEY
            }, signers=[program.provider.wallet.payer]))
            break
        except RPCException as error:
            error_message = _message_from_rpc_error(error)
            is_last_retry = retry == (retries - 1)
            should_retry = error_message == 'Transaction simulation failed: Blockhash not found'
            if should_retry and not is_last_retry:
                continue
            raise error

    await wait_until_accounts_created(program, [game_pda, vault_pda])

    return games_counter


async def start_game(program: Program, game_index: int):
    trivia_pda, _ = _trivia_pda(program.program_id)
    game_pda, _ = _game_pda(program.program_id, trivia_pda, game_index)

    await program.rpc["start_game"](ctx=Context(accounts={
        'game': game_pda,
        'authority': program.provider.wallet.public_key,
        'system_program': SYS_PROGRAM_ID,
    }, signers=[program.provider.wallet.payer], options=TxOpts(preflight_commitment=Confirmed)))


async def add_question(program: Program, game_index: int, keypair: Keypair, text: str, variants: List[str], time: int):
    trivia_pda, trivia_bump = _trivia_pda(program.program_id)
    game_pda, game_bump = _game_pda(program.program_id, trivia_pda, game_index)

    encoded_text = _sequence_sha256([text])
    encoded_variants = [_sequence_sha256([text, variant]) for variant in variants]

    # todo: maybe wait until the transaction is actually confirmed?
    await program.rpc["add_question"](encoded_text, encoded_variants, time, ctx=Context(accounts={
        'game': game_pda,
        'question': keypair.public_key,
        'authority': program.provider.wallet.public_key,
        'system_program': SYS_PROGRAM_ID,
    }, signers=[program.provider.wallet.payer, keypair], options=TxOpts(preflight_commitment=Confirmed)))


async def reveal_question(program: Program, game_index: int, keypair: Keypair, text: str, variants: List[str]):
    trivia_pda, trivia_bump = _trivia_pda(program.program_id)
    game_pda, game_bump = _game_pda(program.program_id, trivia_pda, game_index)

    await program.rpc["reveal_question"](text, variants, ctx=Context(accounts={
        'question': keypair.public_key,
        'game': game_pda,
        'authority': program.provider.wallet.public_key,
        'system_program': SYS_PROGRAM_ID,
    }, signers=[program.provider.wallet.payer], options=TxOpts(skip_preflight=True, preflight_commitment=Confirmed)))


async def reveal_answer(program: Program, game_index: int, keypair: Keypair, answer_variant_id: int):
    trivia_pda, trivia_bump = _trivia_pda(program.program_id)
    game_pda, game_bump = _game_pda(program.program_id, trivia_pda, game_index)

    await program.rpc["reveal_answer"](answer_variant_id, ctx=Context(accounts={
        'question': keypair.public_key,
        'game': game_pda,
        'authority': program.provider.wallet.public_key,
        'system_program': SYS_PROGRAM_ID,
    }, signers=[program.provider.wallet.payer], options=TxOpts(skip_preflight=True, preflight_commitment=Confirmed)))


def _authority_wallet():
    return Wallet(payer=Keypair.from_secret_key(base58.b58decode(os.environ['AUTHORITY_WALLET_PRIVATE_KEY_BASE58'])))


def _idl():
    with Path("idl.json").open() as f:
        raw_idl = json.load(f)
    idl = Idl.from_json(raw_idl)
    return idl


# PDAs: return public keys and bump values

def _trivia_pda(program_id: PublicKey) -> Tuple[PublicKey, int]:
    return PublicKey.find_program_address([TRIVIA], program_id)


def _game_pda(program_id: PublicKey, trivia_pda: PublicKey, game_index: int) -> Tuple[PublicKey, int]:
    return PublicKey.find_program_address([GAME, bytes(trivia_pda), str(game_index).encode('utf-8')], program_id)


def _vault_pda(program_id: PublicKey, game_pda: PublicKey) -> Tuple[PublicKey, int]:
    return PublicKey.find_program_address([VAULT, bytes(game_pda)], program_id)


def _vault_authority_pda(program_id: PublicKey, game_pda: PublicKey) -> Tuple[PublicKey, int]:
    return PublicKey.find_program_address([VAULT_AUTHORITY, bytes(game_pda)], program_id)


def _sequence_sha256(sequence: List[str]) -> bytes:
    accumulated = []
    for i, item in enumerate(sequence):
        if i == 0:
            accumulated.append(hashlib.sha256(item.encode('utf-8')).digest())
        else:
            accumulated.append(hashlib.sha256(accumulated[-1] + item.encode('utf-8')).digest())
    return accumulated[-1]


# asyncio.run(main())
