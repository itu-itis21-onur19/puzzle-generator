import move_node
import chess.engine
import check_validity

# This module defines a MoveTree class that represents a tree of moves in a chess game.
# Each node in the tree corresponds to a specific move, and the tree can be expanded to
# include all possible moves from a given position.
# This class starts from an initialized position from the initialized database.

class MoveTree:
    def __init__(self, root_board):
        self.root = move_node.MoveNode()
        self.board = root_board
        self.root.is_root = True
        self.root.is_leaf = True  # Initially, the root is a leaf node
        self.root.move = None
        self.root.evaluation = root_board.evaluate() if hasattr(root_board, 'evaluate') else None


    def build_tree(self, engine, child_limit = 5, blunder_children_limit=1, depth_limit=10):
        """
        Builds the move tree from the root node, expanding each node to a specified depth.
        Takes top 5 moves as main children and 1 blunder child.
        :param engine: The chess engine used for move analysis.
        :param child_limit: The maximum number of children to expand for each node.
        :param blunder_children_limit: The maximum number of blunder children to expand.
        :param depth_limit: The maximum depth to expand the tree.
        """
        def _build(node, current_depth):
            if current_depth >= depth_limit:
                return

            # dont reconstruct the board, just add the moves by pushing and popping
            board = node.board.copy()
            if node.move:
                board.push(node.move)
            if board.is_game_over():
                return
            node.is_leaf = True
            node.evaluation = board.evaluate() if hasattr(board, 'evaluate') else None
            if not board.turn == chess.WHITE:
                return
            # If the node is not the root, analyze the position
            if not node.is_root:
                # Ensure the board is set to the current position
                board.set_fen(node.board.fen())
            else:
                # For the root node, we already have the board set
                board = self.board.copy()

            # If the board is in a terminal state, return
            if board.is_game_over():
                return 
            
            # If the node is a leaf, we can expand it
            if node.is_leaf:
                # Get legal moves from the board
                legal_moves = list(board.legal_moves)
                for move in legal_moves:
                    child = node.add_child(move)
                    child.board = board.copy()
                    child.board.push(move)
                    child.evaluation = child.board.evaluate() if hasattr(child.board, 'evaluate') else None
                    _build(child, current_depth + 1)

            node.is_leaf = False  # This node will have children
            node.children = []  # Clear any existing children
            node.depth = current_depth    
            # If the node is not the root, analyze the position
            if not node.is_root:
                # Ensure the board is set to the current position
                board.set_fen(node.board.fen())
            else:   
                # For the root node, we already have the board set
                board = self.board.copy()   

            # Get top moves from engine
            results = engine.analyse(board, chess.engine.Limit(time=0.1), multipv=child_limit + blunder_children_limit)
            if not isinstance(results, list):
                results = [results]

            # Add top child_limit moves as main children
            for i, result in enumerate(results[:child_limit]):
                move = result["pv"][0]
                child = node.add_child(move)
                child.evaluation = result["score"].white().score() / 100.0 if not result["score"].is_mate() else None
                child.depth = current_depth + 1
                _build(child, current_depth + 1)

            # Optionally add blunder children (moves that are not among the best)
            for i, result in enumerate(results[child_limit:child_limit + blunder_children_limit]):
                move = result["pv"][0]
                child = node.add_child(move)
                child.evaluation = result["score"].white().score() / 100.0 if not result["score"].is_mate() else None
                child.depth = current_depth + 1
                _build(child, current_depth + 1)

        # Clear any existing tree nodes
        self.root.children = []
        _build(self.root, 0)


    def traverse(self, node=None):
        """
        Traverses the whole move tree starting from the given node.
        checks for valid puzzles in each move node.
        if no valid puzzles are found, it will continue traversing.
        :param node: The current node to start traversal from. If None, starts from the root.
        """
        if node is None:
            node = self.root

        # Check if the current node is a valid puzzle
        if check_validity.is_valid_puzzle(node):
            return self.board.fen()

        # Traverse children nodes
        for child in node.children:
            result = self.traverse(child)
            if result:
                return result

        return None


