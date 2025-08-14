import chess
from chess import Board

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0  # Usually not counted for material
}

def material_difference(board: Board) -> int:
    """
    Calculate the material difference for the given board.
    Positive if white is ahead, negative if black is ahead.
    """
    white_material = 0
    black_material = 0
    for piece_type in PIECE_VALUES:
        white_material += len(board.pieces(piece_type, chess.WHITE)) * PIECE_VALUES[piece_type]
        black_material += len(board.pieces(piece_type, chess.BLACK)) * PIECE_VALUES[piece_type]
    return white_material - black_material

def format_eval_string(score) -> str:
    """
    Formats a python-chess engine score object as a human-readable string.
    Shows mate if available, otherwise centipawn evaluation as a float.
    """
    if score.is_mate():
        mate = score.mate()
        if mate is not None:
            return f"#{mate}"
        else:
            return "#"
    cp = score.white().score()
    if cp is not None:
        return f"{cp / 100.0:+.2f}"
    return "N/A"

def format_eval_float(score) -> float:
    """
    Returns the evaluation as a float (in pawns) from White's perspective.
    If mate is detected, returns a large positive or negative value.
    """
    if score.is_mate():
        mate = score.mate()
        if mate is not None:
            # Use a large value for mate, positive for mate in N, negative for mate in -N
            return 100.0 if mate > 0 else -100.0
        else:
            return 0.0
    cp = score.white().score()
    if cp is not None:
        return cp / 100.0