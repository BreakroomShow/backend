import os
import asyncio
from datetime import datetime, timedelta
from typing import List
import time
import pytz
import sentry_sdk
from solana.keypair import Keypair
from libs import game_state, authority_solana, pusher_client, redis_connection
from models import game, replay


def _get_demo_scenario_1() -> game_state.Scenario:
    tip_1 = game_state.CryptoFact(game_start_offset=0, text='don’t enter your seed phrase anywhere, but trusted wallets')
    tip_2 = game_state.CryptoFact(game_start_offset=10, text='if someone dms you on discord, it’s probably scam')
    tip_3 = game_state.CryptoFact(game_start_offset=20, text='check the urls of the apps you use')
    tip_4 = game_state.CryptoFact(game_start_offset=30, text='use new wallets for untrusted apps')

    intro = game_state.IntroSplash(game_start_offset=40)
    game_info_splash = game_state.GameInfoSplash(game_start_offset=50, players=1000, prize_fund_usd=300, sponsor_title='Dnevnichok')

    question_1 = game_state.Question(
        game_start_offset=60, question='Cristiano Ronaldo plays which sport?',
        answers=['Soccer', 'Basketball', 'Baseball'],
        question_index=0
    )
    answer_reveal_1 = game_state.AnswerReveal(
        game_start_offset=75, question=question_1, correct_answer_ind=0,
        answer_count={0: 100, 1: 75, 2: 50},
        question_index=0
    )
    fact_1 = game_state.QuestionFact(
        game_start_offset=80, text='Ronaldo has made over $1 billion in career earnings, the first team sport athlete to hit the milestone.'
    )

    question_2 = game_state.Question(
        game_start_offset=90, question='Which of these countries is not in Europe?',
        answers=['Zimbabwe', 'France', 'Spain'],
        question_index=1
    )
    answer_reveal_2 = game_state.AnswerReveal(
        game_start_offset=105, question=question_2, correct_answer_ind=0,
        answer_count={0: 100, 1: 75, 2: 50},
        question_index=1
    )
    fact_2 = game_state.QuestionFact(
        game_start_offset=110,
        text='Due to inflation, 100 trillion dollar bills are common in Zimbabwe.'
    )

    question_3 = game_state.Question(
        game_start_offset=120, question='The iPhone is made by which of these companies? ',
        answers=['Apple', 'Ford', 'Lipton'],
        question_index=2
    )
    answer_reveal_3 = game_state.AnswerReveal(
        game_start_offset=135, question=question_3, correct_answer_ind=0,
        answer_count={0: 100, 1: 75, 2: 50},
        question_index=2
    )
    fact_3 = game_state.QuestionFact(
        game_start_offset=140,
        text='Current iPhones have over 100,000x the processing power of the computer on board the Apollo 11 spacecraft. '
    )

    question_4 = game_state.Question(
        game_start_offset=150, question='Which of these comic book characters is a part of the Avengers?',
        answers=['Captain America', 'Superman', 'Charlie Brown'],
        question_index=3
    )
    answer_reveal_4 = game_state.AnswerReveal(
        game_start_offset=165, question=question_4, correct_answer_ind=0,
        answer_count={0: 100, 1: 75, 2: 50},
        question_index=3
    )
    fact_4 = game_state.QuestionFact(
        game_start_offset=170,
        text='Chris Evans turned down the role of Captain America three times before finally donning the iconic stars and stripes.'
    )

    question_5 = game_state.Question(
        game_start_offset=180, question='What song has spent the longest time at #1 on the Billboard Hot 100?',
        answers=['Old Town Road', 'Despactio', 'Uptown Funk'],
        question_index=4
    )
    answer_reveal_5 = game_state.AnswerReveal(
        game_start_offset=195, question=question_5, correct_answer_ind=0,
        answer_count={0: 100, 1: 75, 2: 50},
        question_index=4
    )
    fact_5 = game_state.QuestionFact(
        game_start_offset=200,
        text='Lil Nas X has released 6 official remixes to "Old Town Road", the biggest with Billy Ray Cyrus.'
    )

    question_6 = game_state.Question(
        game_start_offset=210, question='After a kidney transplant, how many kidneys does someone typically have?',
        answers=['3', '2', '1'],
        question_index=5
    )
    answer_reveal_6 = game_state.AnswerReveal(
        game_start_offset=225, question=question_6, correct_answer_ind=0,
        answer_count={0: 100, 1: 75, 2: 50},
        question_index=5
    )
    fact_6 = game_state.QuestionFact(
        game_start_offset=230,
        text='Doctors typically put the third kidney in the patient\'s pelvis, leaving the original two kidneys where they are.'
    )

    question_7 = game_state.Question(
        game_start_offset=240, question='Kim Il-Sung founded which country?',
        answers=['North Korea', 'Singapore', 'Myanmar'],
        question_index=6
    )
    answer_reveal_7 = game_state.AnswerReveal(
        game_start_offset=255, question=question_7, correct_answer_ind=0,
        answer_count={0: 100, 1: 75, 2: 50},
        question_index=6
    )
    fact_7 = game_state.QuestionFact(
        game_start_offset=260,
        text='Kim Il-Sung had a baseball sized tumor on the back of his head, resulting in all propaganda photos taken of him from the left side to cover it up.'
    )

    question_8 = game_state.Question(
        game_start_offset=270, question='What is the name of this iconic 1997 film starring Kate Winslet and Leonardo DiCaprio?',
        answers=['Titanic', 'The Departed', 'Catch Me If You Can'],
        question_index=7
    )
    answer_reveal_8 = game_state.AnswerReveal(
        game_start_offset=285, question=question_8, correct_answer_ind=0,
        answer_count={0: 100, 1: 75, 2: 50},
        question_index=7
    )
    fact_8 = game_state.QuestionFact(
        game_start_offset=290,
        text='Titanic was the highest grossing movie of all time until it was surpassed in 2010 by James Cameron\'s Avatar.'
    )

    question_9 = game_state.Question(
        game_start_offset=300, question='In WWII, the Germans constructed a giant railway gun named what?',
        answers=['Schwerer Gustav', 'Kleiner Goliath', 'Stolz Freude'],
        question_index=8
    )
    answer_reveal_9 = game_state.AnswerReveal(
        game_start_offset=315, question=question_9, correct_answer_ind=0,
        answer_count={0: 100, 1: 75, 2: 50},
        question_index=8
    )
    fact_9 = game_state.QuestionFact(
        game_start_offset=320,
        text='The largest gun ever built, the Gustav could fire 7 ton rounds up to 29 miles away.'
    )

    question_10 = game_state.Question(
        game_start_offset=330, question='What was the name of entertainer Michael Jackson\'s rare skin disease?',
        answers=['Vitiligo', 'Argyria', 'Pemphigus'],
        question_index=9
    )
    answer_reveal_10 = game_state.AnswerReveal(
        game_start_offset=345, question=question_10, correct_answer_ind=0,
        answer_count={0: 100, 1: 75, 2: 50},
        question_index=9
    )
    fact_10 = game_state.QuestionFact(
        game_start_offset=350,
        text='Michael Jackson\'s interview with Oprah where he revealed he had the condition was the most watched interview ever with 90 million viewers.'
    )

    question_11 = game_state.Question(
        game_start_offset=360, question='Which of these animals can dive nearly 20 feet below water for food?',
        answers=['Moose', 'Tortoise', 'Hippopotamus'],
        question_index=10
    )
    answer_reveal_11 = game_state.AnswerReveal(
        game_start_offset=375, question=question_11, correct_answer_ind=0,
        answer_count={0: 100, 1: 75, 2: 50},
        question_index=10
    )
    fact_11 = game_state.QuestionFact(
        game_start_offset=380,
        text='When colder weather comes, moose typically feast on the aquatic vegetation found at the bottom of lakes.'
    )

    question_12 = game_state.Question(
        game_start_offset=390, question='What is the name of the biggest cargo ship in the world?',
        answers=['Ever Ace', 'Ever Aim', 'HMM Algeciras'],
        question_index=11
    )
    answer_reveal_12 = game_state.AnswerReveal(
        game_start_offset=405, question=question_12, correct_answer_ind=0,
        answer_count={0: 100, 1: 75, 2: 50},
        question_index=11
    )
    fact_12 = game_state.QuestionFact(
        game_start_offset=410,
        text='The Ever Ace can hold up to 23,992 containers of cargo, nearly half a million tons.'
    )

    return game_state.Scenario(events=[
        tip_1, tip_2, tip_3, tip_4,
        intro, game_info_splash,
        question_1, answer_reveal_1, fact_1,
        question_2, answer_reveal_2, fact_2,
        question_3, answer_reveal_3, fact_3,
        question_4, answer_reveal_4, fact_4,
        question_5, answer_reveal_5, fact_5,
        question_6, answer_reveal_6, fact_6,
        question_7, answer_reveal_7, fact_7,
        question_8, answer_reveal_8, fact_8,
        question_9, answer_reveal_9, fact_9,
        question_10, answer_reveal_10, fact_10,
        question_11, answer_reveal_11, fact_11,
        question_12, answer_reveal_12, fact_12,
    ])


def _get_demo_scenario_2() -> game_state.Scenario:
    question_1 = game_state.Question(
        game_start_offset=60, question='Cristiano Ronaldo plays which sport?',
        answers=['Soccer', 'Basketball', 'Baseball'],
        question_index=0
    )
    answer_reveal_1 = game_state.AnswerReveal(
        game_start_offset=75, question=question_1, correct_answer_ind=0,
        answer_count={0: 100, 1: 75, 2: 50},
        question_index=0
    )
    return game_state.Scenario(events=[
        question_1,
        answer_reveal_1,
    ])


async def _distribute_chain_event(program: authority_solana.Program, pusher_conn: pusher_client.Pusher,
                                  active_game: game.Game, event: game_state.AnyEvent, question_keypair: Keypair):
    print('[chain_distributing]', event)
    additional_socket_fields = {}

    if event.type == game_state.EventType.question:
        await authority_solana.reveal_question(
            program=program,
            game_index=active_game.game_index,
            keypair=question_keypair,
            text=event.question,
            variants=event.answers,
        )
    elif event.type == game_state.EventType.answer_reveal:
        await authority_solana.reveal_answer(
            program=program,
            game_index=active_game.game_index,
            keypair=question_keypair,
            answer_variant_id=event.correct_answer_ind + 1
        )

    if event.type in [game_state.EventType.question, event.type == game_state.EventType.answer_reveal]:
        additional_socket_fields['question_public_key'] = str(question_keypair.public_key)

    pusher_conn.trigger(active_game.socket_key(), event.type.value, {**event.dict(), **additional_socket_fields})


def _distribute_socket_event(pusher_conn: pusher_client.Pusher, active_game: game.Game, event: game_state.AnyEvent):
    pusher_type = event.type.value
    pusher_data = event.dict()

    if event.type == game_state.EventType.planned_chat_message:
        pusher_type = pusher_client.CHAT_MESSAGE_EVENT_NAME
        pusher_data = event.to_message().dict()

    pusher_conn.trigger(active_game.socket_key(), pusher_type, pusher_data)


def _generate_chat_messages(game_duration: int) -> List[game_state.PlannedChatMessage]:
    planned_messages = []
    for line in open('demo_game_comments.txt'):
        offset, text = line.strip().split(' ', maxsplit=1)
        offset = int(offset)
        if offset > game_duration:
            break
        planned_messages.append(game_state.PlannedChatMessage(
            text=text,
            from_id=str(Keypair.generate().public_key),
            game_start_offset=offset,
        ))
    return planned_messages


def _generate_viewer_counter_updates(
    game_duration: int, update_interval: int, first_question_at: int,
    finish_players: int, max_players: int,
) -> List[game_state.ViewerCountUpdate]:
    updates = []
    current_offset = 0
    while current_offset < game_duration:
        if current_offset < first_question_at:  # X / current_offset = max_players / first_question_at
            viewer_count = current_offset * max_players / first_question_at
        else:  # X / (current_offset - first_question_at) = (max_players - finish_players) / (game_duration - first_question_at)
            decreased_by = (current_offset - first_question_at) * (max_players - finish_players) / (game_duration - first_question_at)
            viewer_count = max_players - decreased_by
        updates.append(game_state.ViewerCountUpdate(game_start_offset=current_offset, viewer_count=int(viewer_count)))
        current_offset += update_interval
    return updates


async def _submit_questions_to_contract(program: authority_solana.Program, game: game.Game,
                                        question_events: List[game_state.Question], question_keypairs: List[Keypair]):
    for i, event in enumerate(question_events):
        await authority_solana.add_question(
            program=program,
            game_index=game.game_index,
            keypair=question_keypairs[i],
            text=event.question,
            variants=event.answers,
            time=12,
        )


async def main():
    sentry_sdk.init(os.environ['SENTRY_URL'], traces_sample_rate=1.0)

    interval = 30
    redis_conn = redis_connection.get()
    pusher_conn = pusher_client.get_pusher_client()

    while True:
        program = await authority_solana.get_program()

        try:
            await (
                (await authority_solana.get_program(official_rpc=True))
                .provider.connection.request_airdrop(program.provider.wallet.public_key, 1_000_000_000)
            )
        except Exception as e:
            print('[airdrop_exception]', e)

        chain_name = 'Test game'
        starts_at = datetime.utcfromtimestamp((int(time.time()) // interval) * interval + interval).replace(tzinfo=pytz.UTC)

        prize_fund = await authority_solana.create_devnet_prize_fund(program, program.provider.wallet.public_key)

        game_index = await authority_solana.create_game(
            program,
            name=chain_name,
            start_time=starts_at + timedelta(seconds=3600),
            prize_fund=prize_fund
        )
        new_game = game.Game(
            id=None,
            chain_name=chain_name,
            chain_start_time=starts_at,
            game_index=game_index,
        )
        game.create(redis_conn, new_game)
        game.mark_current(redis_conn, new_game.id)

        scenario = _get_demo_scenario_2()
        scenario.events = sorted(scenario.events, key=lambda e: e.game_start_offset)
        game_duration = int(scenario.events[-1].game_start_offset + scenario.events[-1].duration)

        scenario.events = sorted(
            scenario.events +
            _generate_chat_messages(
                game_duration=game_duration,
            ) +
            _generate_viewer_counter_updates(
                game_duration=game_duration,
                update_interval=2,
                first_question_at=int(
                    list(filter(lambda event: event.type == game_state.EventType.question, scenario.events))
                    [0].game_start_offset
                ),
                finish_players=102,
                max_players=1021,
            ),
            key=lambda e: e.game_start_offset
        )

        question_events = [event for event in scenario.events if type(event) == game_state.Question]

        question_keypairs = [Keypair.generate() for _ in range(len(question_events))]
        current_question = 0

        await _submit_questions_to_contract(
            program,
            new_game,
            question_events,
            question_keypairs
        )

        await authority_solana.wait_until_accounts_created(program, [keypair.public_key for keypair in question_keypairs])

        actual_start_time = time.time()
        replay.record_start(redis_conn, new_game.id, actual_start_time)

        while scenario.events:
            next_event = scenario.events.pop(0)
            current_offset = time.time() - actual_start_time
            await asyncio.sleep(max(next_event.game_start_offset - current_offset, 0))

            if next_event.distribution_type == game_state.DistributionType.chain:
                await _distribute_chain_event(program, pusher_conn, new_game, next_event, question_keypairs[current_question])
            elif next_event.distribution_type == game_state.DistributionType.socket:
                _distribute_socket_event(pusher_conn, new_game, next_event)

            replay.record_event(redis_conn, new_game.id, time.time(), next_event)
            if next_event.type == game_state.EventType.answer_reveal:
                current_question += 1

        game.remove_current_mark(redis_conn, new_game.id)
        replay.record_finish(redis_conn, new_game.id, time.time())
        replay.set_last(redis_conn, new_game.id)
        await program.close()


if __name__ == '__main__':
    asyncio.run(main(

    ))
