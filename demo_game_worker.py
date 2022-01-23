import asyncio
from datetime import datetime
import time
from libs import game_state, authority_solana, pusher_client, redis_connection
from models import game, replay


def _get_demo_scenario_1() -> game_state.Scenario:
    crypto_fact_1 = game_state.GameInfoSplash(game_start_offset=3, players=1000, prize_fund_usd=300, sponsor_title='Dnevnichok')

    question_1 = game_state.Question(
        game_start_offset=10, question='Cristiano Ronaldo plays which sport?',
        answers=['Soccer', 'Basketball', 'Baseball']
    )
    answer_reveal_1 = game_state.AnswerReveal(
        game_start_offset=25, question=question_1, correct_answer_ind=0
    )
    fact_1 = game_state.QuestionFact(
        game_start_offset=30, text='Ronaldo has made over $1 billion in career earnings, the first team sport athlete to hit the milestone.'
    )

    question_2 = game_state.Question(
        game_start_offset=40, question='Which of these countries is not in Europe?',
        answers=['Zimbabwe', 'France', 'Spain']
    )
    answer_reveal_2 = game_state.AnswerReveal(
        game_start_offset=55, question=question_2, correct_answer_ind=0
    )
    fact_2 = game_state.QuestionFact(
        game_start_offset=60,
        text='Due to inflation, 100 trillion dollar bills are common in Zimbabwe.'
    )

    question_3 = game_state.Question(
        game_start_offset=70, question='The iPhone is made by which of these companies? ',
        answers=['Apple', 'Ford', 'Lipton']
    )
    answer_reveal_3 = game_state.AnswerReveal(
        game_start_offset=85, question=question_3, correct_answer_ind=0
    )
    fact_3 = game_state.QuestionFact(
        game_start_offset=90,
        text='Current iPhones have over 100,000x the processing power of the computer on board the Apollo 11 spacecraft. '
    )

    question_4 = game_state.Question(
        game_start_offset=100, question='Which of these comic book characters is a part of the Avengers?',
        answers=['Captain America', 'Superman', 'Charlie Brown']
    )
    answer_reveal_4 = game_state.AnswerReveal(
        game_start_offset=115, question=question_4, correct_answer_ind=0
    )
    fact_4 = game_state.QuestionFact(
        game_start_offset=120,
        text='Chris Evans turned down the role of Captain America three times before finally donning the iconic stars and stripes.'
    )

    question_5 = game_state.Question(
        game_start_offset=130, question='What song has spent the longest time at #1 on the Billboard Hot 100?',
        answers=['Old Town Road', 'Despactio', 'Uptown Funk']
    )
    answer_reveal_5 = game_state.AnswerReveal(
        game_start_offset=145, question=question_5, correct_answer_ind=0
    )
    fact_5 = game_state.QuestionFact(
        game_start_offset=150,
        text='Lil Nas X has released 6 official remixes to "Old Town Road", the biggest with Billy Ray Cyrus.'
    )

    question_6 = game_state.Question(
        game_start_offset=160, question='After a kidney transplant, how many kidneys does someone typically have?',
        answers=['3', '2', '1']
    )
    answer_reveal_6 = game_state.AnswerReveal(
        game_start_offset=175, question=question_6, correct_answer_ind=0
    )
    fact_6 = game_state.QuestionFact(
        game_start_offset=180,
        text='Doctors typically put the third kidney in the patient\'s pelvis, leaving the original two kidneys where they are.'
    )

    question_7 = game_state.Question(
        game_start_offset=190, question='Kim Il-Sung founded which country?',
        answers=['North Korea', 'Singapore', 'Myanmar']
    )
    answer_reveal_7 = game_state.AnswerReveal(
        game_start_offset=205, question=question_7, correct_answer_ind=0
    )
    fact_7 = game_state.QuestionFact(
        game_start_offset=210,
        text='Kim Il-Sung had a baseball sized tumor on the back of his head, resulting in all propaganda photos taken of him from the left side to cover it up.'
    )

    question_8 = game_state.Question(
        game_start_offset=220, question='What is the name of this iconic 1997 film starring Kate Winslet and Leonardo DiCaprio?',
        answers=['Titanic', 'The Departed', 'Catch Me If You Can']
    )
    answer_reveal_8 = game_state.AnswerReveal(
        game_start_offset=235, question=question_8, correct_answer_ind=0
    )
    fact_8 = game_state.QuestionFact(
        game_start_offset=240,
        text='Titanic was the highest grossing movie of all time until it was surpassed in 2010 by James Cameron\'s Avatar.'
    )

    question_9 = game_state.Question(
        game_start_offset=250, question='In WWII, the Germans constructed a giant railway gun named what?',
        answers=['Schwerer Gustav', 'Kleiner Goliath', 'Stolz Freude']
    )
    answer_reveal_9 = game_state.AnswerReveal(
        game_start_offset=265, question=question_9, correct_answer_ind=0
    )
    fact_9 = game_state.QuestionFact(
        game_start_offset=270,
        text='The largest gun ever built, the Gustav could fire 7 ton rounds up to 29 miles away.'
    )

    question_10 = game_state.Question(
        game_start_offset=280, question='What was the name of entertainer Michael Jackson\'s rare skin disease?',
        answers=['Vitiligo', 'Argyria', 'Pemphigus']
    )
    answer_reveal_10 = game_state.AnswerReveal(
        game_start_offset=295, question=question_10, correct_answer_ind=0
    )
    fact_10 = game_state.QuestionFact(
        game_start_offset=300,
        text='Michael Jackson\'s interview with Oprah where he revealed he had the condition was the most watched interview ever with 90 million viewers.'
    )

    question_11 = game_state.Question(
        game_start_offset=310, question='Which of these animals can dive nearly 20 feet below water for food?',
        answers=['Moose', 'Tortoise', 'Hippopotamus']
    )
    answer_reveal_11 = game_state.AnswerReveal(
        game_start_offset=325, question=question_11, correct_answer_ind=0
    )
    fact_11 = game_state.QuestionFact(
        game_start_offset=330,
        text='When colder weather comes, moose typically feast on the aquatic vegetation found at the bottom of lakes.'
    )

    question_12 = game_state.Question(
        game_start_offset=340, question='What is the name of the biggest cargo ship in the world?',
        answers=['Ever Ace', 'Ever Aim', 'HMM Algeciras']
    )
    answer_reveal_12 = game_state.AnswerReveal(
        game_start_offset=355, question=question_12, correct_answer_ind=0
    )
    fact_12 = game_state.QuestionFact(
        game_start_offset=360,
        text='The Ever Ace can hold up to 23,992 containers of cargo, nearly half a million tons.'
    )

    return game_state.Scenario(events=[
        crypto_fact_1,
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


def _distribute_chain_event(program: authority_solana.Program, event: game_state.AnyEvent):
    pass


def _distribute_socket_event(pusher_conn: pusher_client.Pusher, active_game: game.Game, event: game_state.AnyEvent):
    pusher_conn.trigger(active_game.socket_key(), event.type.value, event.dict())


async def main():
    interval = 600
    redis_conn = redis_connection.get()
    pusher_conn = pusher_client.get_pusher_client()

    while True:
        program = await authority_solana.get_program()

        next_game_start_timestamp = (int(time.time()) // interval) * interval + interval
        new_game = game.Game(id=None, chain_name='Test game', chain_start_time=datetime.utcfromtimestamp(next_game_start_timestamp))
        game.create(redis_conn, new_game)
        # await authority_solana.create_game(
        #     program,
        #     name=new_game.chain_name,
        #     start_time=new_game.chain_start_time,
        # )
        await asyncio.sleep(max(next_game_start_timestamp - time.time(), 0))
        game.mark_current(redis_conn, new_game.id)
        replay.record_start(redis_conn, new_game.id, time.time())

        scenario = _get_demo_scenario_1()
        scenario.events = sorted(scenario.events, key=lambda e: e.game_start_offset)

        while scenario.events:
            next_event = scenario.events.pop(0)
            current_offset = time.time() - next_game_start_timestamp
            await asyncio.sleep(max(next_event.game_start_offset - current_offset, 0))

            if next_event.distribution_type == game_state.DistributionType.chain:
                _distribute_chain_event(program, next_event)
            elif next_event.distribution_type == game_state.DistributionType.socket:
                _distribute_socket_event(pusher_conn, new_game, next_event)

            replay.record_event(redis_conn, new_game.id, time.time(), next_event)

        game.remove_current_mark(redis_conn, new_game.id)
        replay.record_finish(redis_conn, new_game.id, time.time())
        replay.set_last(redis_conn, new_game.id)
        await program.close()


if __name__ == '__main__':
    asyncio.run(main())
