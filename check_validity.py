import chess
import chess.engine

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
                return True
        # If the second move is not mate, check if it's below 4
        if not score2.is_mate():
            eval2 = score2.white().score() / 100.0
            if abs(eval2) < 4.0:
                return True
        return False

    # If not mate, use normal logic
    eval1 = score1.white().score() / 100.0
    eval2 = score2.white().score() / 100.0

    # Check if the second best move is checkmate for the opposite side
    if score2.is_mate():
        mate2 = score2.white().mate()
        if (mate2 is not None and ((mate2 > 0 and eval1 < 0) or (mate2 < 0 and eval1 > 0))):
            return True

    if board.turn == chess.WHITE:
        if eval1 <= 2.0:
            return False
    else:
        if eval1 >= -2.0:
            return False

    if abs(eval1 - eval2) <= 1.5:
        return False
    
    # check if the solution is a piece take move
    # keep checking until the first move is not a piece take
    while board.is_capture(results[0]["pv"][0]):
        # If the first move is a capture, we need to check the next move
        if len(results) < 3:
            return False

    return True

