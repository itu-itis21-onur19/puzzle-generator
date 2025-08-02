import chess
import chess.engine
import check_validity

'''This module defines a MoveNode class that represents a node in a move tree.
Each node corresponds to a specific move in a chess game, and can have child nodes
representing subsequent moves.
class members:
- move: The chess move associated with this node.
- parent: The parent node in the move tree.
- children: A list of child nodes representing possible moves from this node.
- is_root: A boolean indicating if this node is the root of the tree.
- is_leaf: A boolean indicating if this node has no children.
- evaluation: The evaluation score of the move, if available.
'''

class MoveNode:
    def __init__(self, move=None, parent=None):
        self.move = move
        self.parent = parent
        self.children = []
        self.is_root = parent is None
        self.is_leaf = True  # Initially, the node is a leaf node
        self.evaluation = None
        self.depth = 0

    def add_child(self, move):
        child_node = MoveNode(move, parent=self)
        self.children.append(child_node)
        self.is_leaf = False  # Current node is no longer a leaf
        return child_node

    def get_line(self):
        node = self
        moves = []
        while node.parent is not None:
            moves.append(node.board.san(node.move))
            node = node.parent
        return list(reversed(moves))






