# We can define a data structure for representing the MCTS nodes that compose
# the tree. Each MCTS node will track the following properties:
#   - game_state: The current state of the game (board position and next player)
#   - parent: The parent MCTS node that led to this one. We can set parent to
#   None to indicate the root of the tree.
#   - move: The last move that directly led to this node.
#   - children: A list of all child nodes in the tree.
#   - win_counts and num_rollouts: Statistics about the rollouts that started
#   from this node.
#   - unvisited_moves: A list of all legal moves from this position that aren't
#   yet part of the tree. Whenever we add a new node to the tree, we pull one
#   move out of unvisited_moves, generate a new MCTS node for it and add it to
#   the children list.

class MCTSNode(object):

    # Initialization of a node within the tree
    def __init__(self, game_state, parent = None, move = None):
        self.game_state = game_state
        self.parent = parent
        self.move = move
        self.win_counts = {
            Player.black = 0
            Player.white = 0
        }
        self.num_rollouts = 0
        self.children = []
        self.unvisited_moves = game_state.legal_moves()

    # A node can be modified in two ways. We can add a new child to the tree
    def add_random_children(self):
        # Get a random index
        index = random.radint(0, len(self.unvisited_moves) - 1)
        # Get a random move using this index
        new_move = self.unvisited_moves.pop(index)
        # Apply the move and get the new game state
        new_game_state = self.game_state.apply_move(new_move)
        # Get the new node for this game state
        new_node = MCTSNode(new_game_state, self, new_move)
        # Save it as a child
        self.children.append(new_node)
        # Return the new node
        return new_node

    # Or we can update its rollout stats
    def record_win(self, winner):
        # Update the winner count
        self.win_counts[winner] += 1
        # Update the rollout count
        self.num_rollouts += 1

    # Finally we can add three convenience methods to access useful properties
    # of our node:

    #   - can_add_child: reports whether this position has any legal moves that
    #   haven't yet been added to the tree
    def can_add_child(self):
        return len(self.unvisited_moves) > 0

    #   - is_terminal: reports whether the game is over at this node; if so whe
    #   can't search any further from here.
    def is_terminal(self):
        return self.game_state.is_over()

    #   - winning_frac: returns the fraction of rollouts that were won by a
    #   given player.
    def winning_frac(self, player):
        return float(self.win_counts[player])/ float(self.num_rollouts)
