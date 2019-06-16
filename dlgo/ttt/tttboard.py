from dlgo.ttt.ttttypes import Player, Point
import copy


class IllegalMoveError(Exception):
    pass


# Constants such as the board size and the definition of all the 3-length lines
# the players can get in order to win (cols, rows and diagonals)
BOARD_SIZE = 3
ROWS = tuple(range(1, BOARD_SIZE + 1)) # (1, 2, 3)
COLS = tuple(range(1, BOARD_SIZE + 1))
# Top left to lower right diagonal
DIAG_1 = (Point(1, 1), Point(2, 2), Point(3, 3))
# Top right to lower left diagonal
DIAG_2 = (Point(1, 3), Point(2, 2), Point(3, 1))


# The board objects will have similar properties to the Go board
class Board:

    # Initialize the board defining a dictionary which will be the grid
    def __init__(self):
        self._grid = {}

    # The place function will try to place a tile in a point for a player
    def place(self, player, point):
        # Check if the point is within the grid
        assert self.is_on_grid(point)
        # Check that no other tile has been set in this point
        assert self._grid.get(point) is None
        # Assign the player to this point
        self._grid[point] = player

    # Check if the point exists within the board limits
    def is_on_grid(self, point):
        return 1 <= point.row <= BOARD_SIZE and 1 <= point.col <= BOARD_SIZE

    # Get the player assigned to the point or None if the point is still free
    def get(self, point):
        return self._grid.get(point)


# The Move class is used to define a move and initialized with the target point
class Move:
    def __init__(self, point):
        # Target point of the move
        self.point = point

# The game state holds the situation as in the game state for the Go game
class GameState:

    # We initialize an state with a board, the player that moves next and the
    # last moved that occured
    def __init__(self, board, next_player, move):
        self.board = board
        self.next_player = next_player
        self.last_move = move

    # Applying a move is the same as in Go, we return a new state with the move
    # having been done
    def apply_move(self, move):
        # Copy the board
        next_board = copy.deepcopy(self.board)
        # Place the tile
        next_board.place(self.next_player, move.point)
        # Return a new state with the new board, change the player's turn and
        # save the last move
        return GameState(next_board, self.next_player.other, move)

    # Starts a new game with an empty board and x as the first Player
    @classmethod
    def new_game(cls):
        board = Board()
        return GameState(board, Player.x, None)

    # Check if a move is valid
    def is_valid_move(self, move):
        # Is valid if the game has not ended and the point is empty
        return (self.board.get(move.point) is None and not self.is_over())

    # Check valid moves and returns an array with posible moves
    def legal_moves(self):
        moves = []
        for row in ROWS:
            for col in COLS:
                move = Move(Point(row, col))
                if self.is_valid_move(move):
                    moves.append(move)
        return moves

    # Checks if the game is over
    def is_over(self):
        # If Player x has 3 in a row, the game ends
        if self._has_3_in_a_row(Player.x):
            return True
        # If Player o has 3 in a row, the game ends
        if self._has_3_in_a_row(Player.o):
            return True
        # If no player has won but all the points are occupied, the game ends
        if all(self.board.get(Point(row, col)) is not None
               for row in ROWS
               for col in COLS):
            return True
        # False if we can keep playing
        return False

    # Check if a player has 3 in a row checking all posibilities
    def _has_3_in_a_row(self, player):
        # Vertical
        for col in COLS:
            if all(self.board.get(Point(row, col)) == player for row in ROWS):
                return True
        # Horizontal
        for row in ROWS:
            if all(self.board.get(Point(row, col)) == player for col in COLS):
                return True
        # Diagonal UL to LR
        if self.board.get(Point(1, 1)) == player and \
                self.board.get(Point(2, 2)) == player and \
                self.board.get(Point(3, 3)) == player:
            return True
        # Diagonal UR to LL
        if self.board.get(Point(1, 3)) == player and \
                self.board.get(Point(2, 2)) == player and \
                self.board.get(Point(3, 1)) == player:
            return True
        return False

    # Determine the winner that can be None if the game ends in a draw
    def winner(self):
        if self._has_3_in_a_row(Player.x):
            return Player.x
        if self._has_3_in_a_row(Player.o):
            return Player.o
        return None
