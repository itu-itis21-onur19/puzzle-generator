# this module stores the initialization of the game
# it creates a randomized game until move 15
# then it returns the board after 15 moves
# does this n times
# and stores the boards in a database

import sqlite3
import initialize
import chess.engine

def store_init_games(engine, db_path, num_games=100):
    """
    Stores a specified number of initialized games in a SQLite database.
    Adds columns for puzzle status and puzzle string.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist, with status and puzzle columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fen TEXT NOT NULL,
            status BOOLEAN,
            puzzle TEXT
        )
    ''')
    
    for _ in range(num_games):
        board = initialize.random_game(engine, max_moves=30)
        cursor.execute(
            'INSERT INTO games (fen, status, puzzle) VALUES (?, NULL, NULL)',
            (board.fen(),)
        )

    print(f"Stored {num_games} initialized games in the database at {db_path}.")
    
    conn.commit()
    conn.close()


# Initialize the chess engine
engine = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")
engine.configure({"Threads": 16, "Hash": 64})  # Configure the engine as needed

# Select the first position from the database
db_path = "initialized_games.db"
store_init_games(engine, db_path)



