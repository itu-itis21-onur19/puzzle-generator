import chess
import chess.engine
import sqlite3
import pgn
import chess.pgn
import time
import image

def generate_puzzle():
    # Initialize the chess board
    board = chess.Board()

    # Initialize the chess engine
    engine = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish") 
    engine.configure({"Threads": 16, "Hash": 64})  # Configure the engine as needed

    # Select the first position from the database
    db_path = "initialized_games.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Fetch the first game that is not a puzzle status is not 1, also fetch the id
    cursor.execute("SELECT fen, id FROM games WHERE status is NULL OR status = 0 LIMIT 1")
    row = cursor.fetchone()

    # If a game is found, set the board to that position
    if row:
        fen = row[0]
        game_id = row[1]
        board.set_fen(fen)
    else:
        print("No games found in the database. Do you want to give a FEN string? (yes/no)")
        response = input().strip().lower()
        if response == "yes":
            fen = input("Enter the FEN string: ").strip()
            try:
                board.set_fen(fen)
            except ValueError as e:
                print(f"Invalid FEN string: {e}")
                conn.close()
                engine.quit()
                exit()
        conn.close()
        engine.quit()
        exit()



    # Generate a puzzle from the current position
    game = chess.pgn.Game()
    game.setup(board)
    game.headers["Event"] = "Puzzle Generation"
    game.headers["Site"] = "Local"
    game.headers["Date"] = time.strftime("%Y.%m.%d")
    game.headers["Id"] = str(game_id)


    # start timer
    start_time = time.time()

    # Generate a puzzle from the current position
    puzzle = pgn.search_puzzle(game, engine, depth=10)  # Adjust depth as needed

    # end timer
    end_time = time.time()
    game.headers["Time"] = f"{end_time - start_time:.2f} seconds"

    if puzzle:
        print("Generated Puzzle FEN:", puzzle)
        # Save the puzzle to the database first row, dont insert but update, set status to 1
        cursor.execute("UPDATE games SET puzzle = ?, status = 1 WHERE id = ?", (puzzle, game_id))
        cursor.execute("UPDATE games SET tries = tries + 1 WHERE id = ?", (game_id,))
        cursor.execute("UPDATE games SET time = time + ? WHERE id = ?", (round(end_time - start_time, 2), game_id))
    else:
        print("No valid puzzle could be generated from the current position.")
        cursor.execute("UPDATE games SET status = 0 WHERE id = ?", (game_id,))
        cursor.execute("UPDATE games SET tries = tries + 1 WHERE id = ?", (game_id,))
        cursor.execute("UPDATE games SET time = time + ? WHERE id = ?", (round(end_time - start_time, 2), game_id))
    conn.commit()

    # open the puzzle in a browser
    if puzzle:
        image.fen_to_image(puzzle)
        # save the game to a PGN file
        with open("generated_puzzle.pgn", "a") as pgn_file:
            pgn_file.write(str(game))
            pgn_file.write(f"\n{puzzle}\n")
            # Add extra newline for separation
            pgn_file.write("\n\n\n")
        print("Puzzle saved to generated_puzzle.pgn")



    # Quit the engine
    engine.quit()
    # Close the database connection
    conn.close()

generate_puzzle()






