import chess
import chess.engine
import chess.pgn
import random
import check_validity

'''
The algorithm:
if white to move:
    play the best move that does not exceed 2.0
if black to move:
    play the best 3 moves as variations
    play one random move out of the legal moves, check if it is valid
    dont branch the random move, only branch 3 moves
'''

def build_tree(game, node, engine, depth=10):
    # Initialize the game with the current board position
    if not game:
        game = chess.pgn.Game()
        game.setup(chess.Board())
    
    if not node:
        node = game

    # for loop of depth
    for _ in range(depth):
        white_results = engine.analyse(node.board(), chess.engine.Limit(time=0.1), multipv=3)
        # if the score is better then 1.5, add the 2nd best move
        best_score = white_results[0]["score"].white().score()
        if best_score is not None and best_score > 150:
            # check if the position is a puzzle
            if check_validity.isValidPuzzle(node.board(), engine, time_limit=0.1):
                # if a puzzle is found while building the tree, return the game
                print("Puzzle found in the main branch.")
                print(node.board().fen())
                print(game)
                return node
            # if the score is better than 3.5, add the third best move
            if best_score is not None and best_score > 350:
                node = node.add_main_variation(white_results[2]["pv"][0])
            # if the score is not better than 1.5, add the second best move
            elif best_score is not None and best_score > 150:
                node = node.add_main_variation(white_results[1]["pv"][0])
            # else add the best move
            else:
                node = node.add_main_variation(white_results[0]["pv"][0])

        temp_node = node # temp node on black's turn
        black_results = engine.analyse(node.board(), chess.engine.Limit(time=0.1), multipv=3)
        ''''''
        # continue from a random selection of the first 3 variations
        length = len(black_results)
        if length < 3:
            temp_node.add_main_variation(black_results[0]["pv"][0])
        else:
            rand = random.choice([0, 1, 2])
            if rand == 0:
                temp_node.add_main_variation(black_results[0]["pv"][0])
            elif rand == 1:  # add the second best move
                score = black_results[1]["score"].white().score()
                if score is not None and score < 150 and len(black_results) > 1:
                    temp_node.add_main_variation(black_results[1]["pv"][0])
                else:
                    temp_node.add_main_variation(black_results[0]["pv"][0])
            elif rand == 2:  # add the third best move
                score = black_results[2]["score"].white().score()
                if score is not None and score < 150 and len(black_results) > 2:
                    temp_node.add_main_variation(black_results[2]["pv"][0])
                else:
                    temp_node.add_main_variation(black_results[0]["pv"][0])


        # add a random move
        legal_moves = list(temp_node.board().legal_moves)
        if legal_moves:
            random_move1 = random.choice(legal_moves)
            random_move2 = random.choice(legal_moves)
            temp_node.add_variation(random_move1)
            temp_node.add_variation(random_move2)
        
        node = temp_node.variation(0)  # Move to the first variation for the next iteration
    return game

def search_puzzle_in_branch(node, engine, depth=10):
    if depth <= 0:
        return None

    # Check if the first variation exists
    if len(node.variations) == 0:
        return None

    node = node.variation(0)  # Start with the first variation, white moves

    # Check if the 1st variation (random move) exists
    if len(node.variations) > 2:
        puzzle_found = check_validity.isValidPuzzle(node.variation(1).board(), engine, time_limit=0.1)
        if puzzle_found:
            return node.variation(1)
        puzzle_found = check_validity.isValidPuzzle(node.variation(2).board(), engine, time_limit=0.1)
        if puzzle_found:
            return node.variation(2)

    # Only recurse if the first variation exists
    if len(node.variations) > 0:
        return search_puzzle_in_branch(node.variation(0), engine, depth - 1)
    else:
        return None


def search_puzzle(game, engine, depth=10):
    node = game

    # Build the game tree
    node = build_tree(game, node, engine, depth)

    # check if the main branch is a valid puzzle
    if check_validity.isValidPuzzle(node.board(), engine, time_limit=0.1):
        print("Puzzle found in the main branch.")
        return node.board().fen()


    # check the main branch
    puzzle = search_puzzle_in_branch(node, engine, depth)
    if puzzle:
        print("Puzzle found in the main branch.")
        print(game)
        return puzzle.board().fen()  # Return the FEN string of the puzzle

    print(game)
    return None  # No valid puzzle found in the main branch or its variations
