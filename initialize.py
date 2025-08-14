'''
This module makes a randomized game until move 15.
for 15 moves:
I will choose randomly from the top moves of white such that (best move - candidate move < 0.3)
I will choose randomly from the top moves of black such that (best move - candidate move < 0.5)
I will make sure that the evaluation stays between -2 and 2.
	by doing so I will make sure that white is a little bit better than black.
I wont use a move tree, because i will just have a single line of moves.
I will return the board after 15 moves.
'''

import chess.engine
import random

def random_game(engine, max_moves=30): #returns the board after 15 full moves
    board = chess.Board()
    move_count = 0
    while move_count < max_moves and not board.is_game_over():
        if board.turn == chess.WHITE:
            # Get top moves for white
            results = engine.analyse(board, chess.engine.Limit(time=0.1), multipv=10)
            candidates = []
            base_score = results[0]["score"].white().score()
            for move in results:
                move_score = move["score"].white().score()
                if move_score is not None and base_score is not None:
                    if abs(move_score - base_score) < 30:
                        candidates.append(move)
            # Optionally, handle mate scores if needed
            if not candidates:
                candidates = [move for move in results if move["score"].white().is_mate()]

        else:
            # Get top moves for black
            results = engine.analyse(board, chess.engine.Limit(time=0.1), multipv=10)
            candidates = []
            base_score = results[0]["score"].black().score()
            for move in results:
                move_score = move["score"].black().score()
                if move_score is not None and base_score is not None:
                    if abs(move_score - base_score) < 50:
                        candidates.append(move)
            # Optionally, handle mate scores if needed
            if not candidates:
                candidates = [move for move in results if move["score"].black().is_mate()]

        if not candidates:
            break

        move = random.choice(candidates)["pv"][0]
        board.push(move)
        move_count += 1

    return board
