import chess
import chess.engine
import utils

STOCKFISH_PATH = "/opt/homebrew/bin/stockfish"

def format_eval(score):
    if score.is_mate():
        mate = score.white().mate()
        if mate is not None:
            return f"Mate in {mate}"
        else:
            return "Mate"
    else:
        cp = score.white().score()
        eval_float = cp / 100.0
        return f"{eval_float:.2f}"

def isValidPuzzle(board, engine, time_limit=0.1):
    """
    Checks if the side to move is better than 2.0 (white >2.0, black <-2.0)
    and if the difference between the top two moves is greater than 1.5.
    If there is a mate, checks if the second best move is below 4.0 or is mate for the opposite side.
    If both moves are mate for the same side, do not accept.
    """
    results = engine.analyse(board, chess.engine.Limit(time=time_limit), multipv=2)
    if not isinstance(results, list):
        results = [results]
    if len(results) < 2:
        return False  # Not enough moves to compare

    score1 = results[0]["score"]
    score2 = results[1]["score"]

    # print move1-score1 and move2-score2
    move1 = results[0]["pv"][0]
    move2 = results[1]["pv"][0]
    print(f"Move 1: {move1}, Score 1: {format_eval(score1)}")
    print(f"Move 2: {move2}, Score 2: {format_eval(score2)}")

    # If the best move is mate
    if score1.is_mate():
        mate1 = score1.white().mate()
        # If the second move is also mate for the same side, do not accept
        if score2.is_mate():
            mate2 = score2.white().mate()
            if mate1 is not None and mate2 is not None and ((mate1 > 0 and mate2 > 0) or (mate1 < 0 and mate2 < 0)):
                return False
        # If the second move is mate for the opposite side, accept
        if score2.is_mate():
            mate2 = score2.white().mate()
            if mate1 is not None and mate2 is not None and ((mate1 > 0 and mate2 < 0) or (mate1 < 0 and mate2 > 0)):
                print(f"Answer: {{ {move1} }}")
                return True
        # If the second move is not mate, check if it's below 4
        if not score2.is_mate():
            eval2 = score2.white().score() / 100.0
            if abs(eval2) < 4.0:
                print(f"Answer: {{ {move1} }}")
                return True
        return False

    # If not mate, use normal logic
    eval1 = score1.white().score() / 100.0
    eval2 = score2.white().score() / 100.0

    # Check if the second best move is checkmate for the opposite side
    if score2.is_mate():
        mate2 = score2.white().mate()
        if (mate2 is not None and ((mate2 > 0 and eval1 < 0) or (mate2 < 0 and eval1 > 0))):
            print(f"Answer: {{ {move1} }}")
            return True

    if board.turn == chess.WHITE:
        if eval1 <= 2.0:
            return False
    else:
        if eval1 >= -2.0:
            return False

    if abs(eval1 - eval2) <= 1.5:
        return False

    
    if board.is_capture(results[0]["pv"][0]):

        # if mate, we can accept it
        if results[0]["score"].is_mate():
            print(f"Answer: {{ {move1} }}")
            return True
        
        # if check, we can accept it
        board.push(results[0]["pv"][0])
        if board.is_check():
            print(f"Answer: {{ {move1} }}")
            return True
        
        # if the next move can also be a puzzle, we can accept it
        results = engine.analyse(board, chess.engine.Limit(time=0.1), multipv=5) # best 5 moves

        # try to play a capture move
        for result in results:
            if board.is_capture(result["pv"][0]):
                # If the next move is a capture, we can accept it
                board.push(result["pv"][0])
                return isValidPuzzle(board, engine, time_limit)
            
        # if no capture move is found, we can still accept the puzzle if it is a valid puzzle
        board.push(results[0]["pv"][0])
        return isValidPuzzle(board, engine, time_limit)

    # If all checks passed, the puzzle is valid
    return True

if __name__ == "__main__":
    # Example usage
    board = chess.Board()
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    board.set_fen("5k2/p3r1R1/1p1Q1p1p/8/P6q/2P5/1PP5/1K6 b - - 0 36")  # Example FEN
    
    if isValidPuzzle(board, engine):
        print("Valid puzzle")
    else:
        print("Invalid puzzle")
    
    engine.quit()
