import asyncio
import json
from pathlib import Path
import os
from typing import Tuple
from datetime import datetime
import base58
from solana.rpc.async_api import AsyncClient
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.system_program import SYS_PROGRAM_ID, transfer, TransferParams
from solana.rpc.types import TxOpts
from solana.transaction import Transaction
from anchorpy import Program, Provider, Wallet, Idl, Context

_DEVNET_DEPLOYED_PROGRAM_ID = "F6JZ61gqo32Mwv4XBwGsVmamsaZCgyVoz8VUvefsqUhm"

TRIVIA = b'trivia'
GAME = b'game'
USER = b'user'
PLAYER = b'player'


async def main():
    client = AsyncClient("https://api.devnet.solana.com")
    provider = Provider(client, _authority_wallet())
    program_id = PublicKey("F6JZ61gqo32Mwv4XBwGsVmamsaZCgyVoz8VUvefsqUhm")
    program = Program(_idl(), program_id, provider)
    # Execute the RPC.
    await program.rpc["initialize"]()
    # Close the underlying http client, otherwise we get warnings.
    await program.close()


async def get_program() -> Program:
    client = AsyncClient("https://api.devnet.solana.com")
    provider = Provider(client, _authority_wallet(), TxOpts())
    program_id = PublicKey(_DEVNET_DEPLOYED_PROGRAM_ID)
    program = Program(_idl(), program_id, provider)


    # instruction = transfer(TransferParams(
    #     from_pubkey=PublicKey('5GS7AaArNZ7L777SUj2NN12phRjj44GMM2gFM3vmzsdA'),
    #     to_pubkey=PublicKey('56NjiE3vSnGWmu4Cmq4k5dA6oL4ZkAvD1TRdizxxXrnW'),
    #     lamports=10000
    # ))
    # transaction = Transaction()
    # transaction.add(instruction)
    # result = await provider.send(transaction, signers=[provider.wallet.payer])
    # print(result)

    # await program.rpc["initialize"](trivia_bump, ctx=Context(accounts={
    #     'trivia': trivia_pda,
    #     'authority': provider.wallet.public_key,
    #     'system_program': SYS_PROGRAM_ID
    # }, signers=[provider.wallet.payer]))

    return program


async def create_game(program: Program, name: str, start_time: datetime):
    return  # FIXME
    trivia_pda, trivia_bump = _trivia_pda(program.program_id)
    games_counter = (await program.account['Trivia'].fetch(trivia_pda)).games_counter

    print(program.program_id, trivia_pda, games_counter)

    game_pda, game_bump = _game_pda(program.program_id, trivia_pda, games_counter)

    options = program.type['GameOptions'](name=name, start_time=int(start_time.timestamp()))

    result = await program.rpc["create_game"](options, game_bump, ctx=Context(accounts={
        'trivia': trivia_pda,
        'game': game_pda,
        'authority': program.provider.wallet.public_key,
        'system_program': SYS_PROGRAM_ID,
    }, signers=[program.provider.wallet.payer]))

    print(result)


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


# asyncio.run(main())
