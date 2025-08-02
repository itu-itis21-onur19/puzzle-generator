'''
First initializing 100 positions from the database.
Then expanding the tree from each position to a specified depth.
The tree is built using the MoveNode class, which represents each move as a node in the tree.
The MoveTree class manages the root node and provides methods to expand the tree.
'''

import move_node
import move_tree
import chess.engine
import sqlite3
import initialize
import check_validity
import chess
import random
import os
import store_init

# initialize the chess engine
def initialize_engine():
    engine_path = "/opt/homebrew/bin/stockfish"  # Adjust this path to your Stockfish binary
    if not os.path.exists(engine_path):
        raise FileNotFoundError(f"Engine not found at {engine_path}")
    return chess.engine.SimpleEngine.popen_uci(engine_path)


engine = initialize_engine()

# Connect to the SQLite database
db_path = "initialized_games.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fen TEXT NOT NULL
    )
''')  

# the db is already filled with 100 games
# Fetch the first game from the database
cursor.execute('SELECT fen FROM games LIMIT 1')
row = cursor.fetchone()
if row:
    initial_fen = row[0]
    root_board = chess.Board(initial_fen)
else:
    print("No games found in the database. Please initialize the database first.")
    root_board = chess.Board()

# Commit the changes and close the connection
conn.commit()
conn.close()

# Create a MoveTree instance with the root board
move_tree_instance = move_tree.MoveTree(root_board)
# Expand the tree to a specified depth
depth_limit = 10 # You can adjust this depth limit as needed
move_tree_instance.root.expand(engine, depth_limit=depth_limit)

# try to find a valid puzzle for the expanded tree
# This will check each child node of the root for validity
# and store valid puzzles in a list
valid_puzzles = []
for child in move_tree_instance.root.children:
    if check_validity.isValidPuzzle(child.board, engine):
        valid_puzzles.append(child)
# Print the valid puzzles found
print(f"Found {len(valid_puzzles)} valid puzzles:")
for puzzle in valid_puzzles:
    print(f"Puzzle FEN: {puzzle.board.fen()}")
    print(f"Moves: {puzzle.get_line()}")



