import chess
import chess.svg
import webbrowser
import sqlite3

# this code converts fen puzzle to image and opens it in a browser
def fen_to_image(fen):
    board = chess.Board(fen)
    svg = chess.svg.board(board=board, size=400)
    
    # Save the SVG to a file
    with open("board.svg", "w") as f:
        f.write(svg)

    # Open the SVG file in the default web browser
    webbrowser.open("board.svg")

def open_puzzle_from_db(puzzle_id):
    # Fetch the puzzle from the database using the puzzle_id
    fen = fetch_fen_from_db(puzzle_id)
    if fen:
        fen_to_image(fen)
    else:
        print("Puzzle not found.")

def fetch_fen_from_db(puzzle_id):
    db_path = "initialized_games.db"  # Adjust the path to your database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT fen FROM puzzles WHERE id = ?", (puzzle_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return row[0]
    else:
        return None
    
if __name__ == "__main__":
    # Example usage
    puzzle_id = input("Enter the puzzle ID: ")
    open_puzzle_from_db(puzzle_id)
