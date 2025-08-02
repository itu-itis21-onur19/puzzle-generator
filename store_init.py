# this module stores the initialization of the game
# it creates a randomized game until move 15
# then it returns the board after 15 moves
# does this n times
# and stores the boards in a database

import sqlite3
import initialize

def store_init_games(engine, db_path, num_games=100):
    """
    Stores a specified number of initialized games in a SQLite database.
    
    :param engine: The chess engine to use for generating moves.
    :param db_path: Path to the SQLite database file.
    :param num_games: Number of games to generate and store.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fen TEXT NOT NULL
        )
    ''')
    
    for _ in range(num_games):
        board = initialize.random_game(engine, max_moves=30)
        cursor.execute('INSERT INTO games (fen) VALUES (?)', (board.fen(),))

    print(f"Stored {num_games} initialized games in the database at {db_path}.")
    
    conn.commit()
    conn.close()



