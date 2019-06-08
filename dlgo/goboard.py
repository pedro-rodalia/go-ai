from dlgo.gotypes import Player
from dlgo import zobrist
import copy

# We need a structure to represent the actions a player can take on a turn
# Normally, a turn involves placing a stone on the board, but a player can
# also pass or resign at any time. Following American Go Association (AGA)
# conventions, we use the term move to mean any of those three actions, wheras
# a play refers to placing a stone. In the move class we therefore encode all
# three types of move (play, pass, resign) and make sure a move has precisely
# one of these types. For actual plays we need to pass a Point to be placed

# A Move is any action a player can play on a turn
class Move():

    # Clients generally won't call the Move constructor directly. Instead,
    # we usually call Move.play, Move.resign or Move.pass to construct an
    # instance of a Move
    def __init__(self, point = None, is_pass = False, is_resign = False):
        # Make sure the move has one of the three types
        assert (point is not None) ^ is_pass ^ is_resign
        self.point = point
        # If point is set, the move is play
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    # This move places a stone on the board
    @classmethod
    def play(cls, point):
        return Move(point = point)

    # This move passes
    @classmethod
    def pass_turn(cls):
        return Move(is_pass = True)

    # This move resigns the current game
    @classmethod
    def resign(cls):
        return Move(is_resign = True)


# We'll keep track of groups of connected stones of the same color and their
# liberties at the same time. Doing so is much more efficient when implementing
# game logic. We call a group of connected stones of the same color a string.
# We can build this structure efficiently with the Python set type

# Go strings are a chain of connected stones of the same color
class GoString():

    # In this version we will use a frozenset for the liberties and the stones
    # to make them immutables, so we need to create a new set instead of
    # modifying the existing ones
    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = frozenset(stones)
        self.liberties = frozenset(liberties)

    # The without_liberty method replaces the previous remove_liberty method
    # in order to account for immutable state
    def without_liberty(self, point):
        new_liberties = self.liberties - set([point])
        return GoString(self.color, self.stones, new_liberties)

    # The with_liberty method replaces the previous add_liberty method
    # in order to account for immutable state
    def with_liberty(self, point):
        new_liberties = self.liberties | set([point])
        return GoString(self.color, self.stones, new_liberties)

    # Returns a new Go string containing all stones in both strings
    def merged_with(self, go_string):
        # Check tha both strings belong to the same player
        assert go_string.color == self.color
        combined_stones = self.stones | go_string.stones
        return GoString(
            self.color,
            combined_stones,
            (self.liberties | go_string.liberties) - combined_stones)

    # Counts the number of liberties within the go string
    @property
    def num_liberties(self):
        return len(self.liberties)

    # Checks if two go strings are the same by comparing colors, stones and
    # liberties
    def __eq__(self, other):
        return isinstance(other, GoString) and \
            self.color == other.color and \
            self.stones == other.stones and \
            self.liberties == other.liberties


# We allow boards to have any number of rows or columns by instantiating them
# with num_rows and num_cols appropiately. To keep track of the board state
# internally, we use the private variable _grid, a dictionary we use to store
# strings of stones
class Board():

    # A board is initialized as an empty grid with the specified number
    # of rows and columns
    def __init__(self, num_rows = 19, num_cols = 19):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self._grid = {}
        # We now instantiate the board with the hash value for an empty board
        self._hash = zobrist.EMPTY_BOARD

    # Board method used for placing stones
    def place_stone(self, player, point):

        # Check that the given point fits in the grid
        assert self.is_on_grid(point)
        # Check that the given point has not been set yet
        assert self._grid.get(point) is None
        # Define variables for storing neighbours and liberties
        adjacent_same_color = []
        adjaceent_opposite_color = []
        liberties = []

        # Visit the given point neighbours
        for neighbour in point.neighbours():
            # Skip loop for neighbours outside the grid
            if not self.is_on_grid(neighbour):
                continue
            neighbour_string = self._grid.get(neighbour)
            # if neighbour is empty, save it as a liberty
            if neighbour_string is None:
                liberties.append(neighbour)
            # If it's a stone of the player's color
            elif neighbour_string.color == player:
                # And it's not yet added to adjacent stones
                if neighbour_string not in adjacent_same_color:
                    adjacent_same_color.append(neighbour_string)
            # If it's an enemy stone
            else:
                # And it's not yet added to adjacent enemy stones
                if neighbour_string not in adjaceent_opposite_color:
                    adjaceent_opposite_color.append(neighbour_string)

        # Create a new string with just the new point and its liberties
        new_string = GoString(player, [point], liberties)

        # Merge any adjacent strings of the same color
        for same_color_string in adjacent_same_color:
            new_string = new_string.merged_with(same_color_string)

        # For each stone in the new string you change the grid reference of the
        # stone point to the new_string reference
        for new_string_point in new_string.stones:
            self._grid[new_string_point] = new_string

        # We apply the hash code for this point and player
        self._hash ^= zobrist.HASH_CODE[point, player]

        # Reduce liberties of any adjacent strings of the opposite color
        for other_color_string in adjaceent_opposite_color:
            replacement = other_color_string.without_liberty(point)
            # If replacement still has liberties replace the string
            if replacement.num_liberties:
                self._replace_string(replacement)
            # Else remove the string
            else:
                self._remove_string(other_color_string)

        # If any opposite-color strings now have zero liberties, remove them
        for other_color_string in adjaceent_opposite_color:
            if other_color_string.num_liberties == 0:
                self._remove_string(other_color_string)

    # Board method used to determine if a point is within the grid limits
    def is_on_grid(self, point):
        return 1 <= point.row <= self.num_rows and \
            1 <= point.col <= self.num_cols

    # Board method to check if the grid point is already taken by another stone
    # Returns the content of a point on the board (a Player if a stone is on
    # that point and None otherwise)
    def get(self, point):
        string = self._grid.get(point)
        # Returns none if the point isn't taken
        if string is None:
            return None
        # Returns the player that has taken the point
        return string.color

    # Board method to get a entire stone string if the point is taken. Returns
    # the entier string of stones at a point (a GoString if a stone is on that
    # point or None otherwise)
    def get_go_string(self, point):
        string = self._grid.get(point)
        # Returns none if the point isn't taken
        if string is None:
            return None
        # Returns the goString for the stone taking the point
        return string

    # To remove a stone, we apply its hash to the board once again. This new
    # helper method updates our board grid with the replacement string
    def _replace_string(self, new_string):
        for point in new_string.stones:
            self._grid[point] = new_string

    # We have to keep in mind that other stones might gain liberties when
    # removing an enemy string
    def _remove_string(self, string):
        # For each point which belonged to the string
        for point in string.stones:
            # For each neighbour of this point
            for neighbour in point.neighbours():
                # Get the string that contains this neighbour
                neighbour_string = self._grid.get(neighbour)
                # If neighbour contains no stones skip a loop
                if neighbour_string is None:
                    continue
                # If is not the same string we are checking
                if neighbour_string is not string:
                    # replace the string with a new string with more liberties
                    self._replace_string(neighbour_string.with_liberty(point))
            # Clear the point within the grid
            self._grid[point] = None
            # With zobrist hashing we need to unapply the hash for this move
            self._hash ^= zobrist.HASH_CODE[point, string.color]

    # Utility method that returns the current Zobrist hash
    def zobrist_hash(self):
        return self._hash


# GameState knows about the board position, the next payer, the previous game
# state, and the last move that has been played
class GameState():

    # Initializes the GameState using params
    def __init__(self, board, next_player, previous, move):
        self.board = board
        self.next_player = next_player
        self.previous_state = previous
        if self.previous_state is None:
            # Initialize previous states as an empty frozenset on first init
            self.previous_states = frozenset()
        else:
            # Or else as a filled frozenset with previous frozenset and current
            # state pair with the color of the player and the Zobrist hash of
            # the previous game state.
            self.previous_states = frozenset(
                previous.previous_states |
                {(previous.next_player, previous.board.zobrist_hash())})
        self.last_move = move

    # Returns the new GameState after applying the move
    def apply_move(self, move):
        # If the move implies changes
        if move.is_play:
            # Duplicate the board to keep the previous state
            next_board = copy.deepcopy(self.board)
            # place the stone from the player on the point
            next_board.place_stone(self.next_player, move.point)
        else:
            # Else use the same board state
            next_board = self.board
        # Return GameState with the new board and the other player
        return GameState(next_board, self.next_player.other, self, move)

    # Method used to start a new game
    @classmethod
    def new_game(cls, board_size):
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)

    # Method used to decide when a game is over
    def is_over(self):
        # If last move was
        if self.last_move is None:
            return False
        # If last move was resign, return true as the game is over
        if self.last_move.is_resign:
            return True
        # Save last move from previous state
        second_last_move = self.previous_state.last_move
        if second_last_move is None:
            return False
        # If both last and second last moves are pass, end the game
        return self.last_move.is_pass and second_last_move.is_pass

    # Enforcing the self-capture rule by applying the move to a copy of the
    # board and checking the number of liberties afterwards
    def is_move_self_capture(self, player, move):
        # If the game is not a play, return False
        if not move.is_play:
            return False
        # Get a new board where the play will be applied
        next_board = copy.deepcopy(self.board)
        # Apply the play and check if is a valid play
        next_board.place_stone(player, move.point)
        # Get the string that forms the newly played stone
        new_string = next_board.get_go_string(move.point)
        # If the string has no liberties return True, else return False
        return new_string.num_liberties == 0

    # The rule for preventing kos will be that a player may not play a stone
    # that would recreate a previous game state, where the game state includes
    # both the stones on the board and the player whose turn is next. Because
    # each GameState instance keeps a pointer to the previous state, we can
    # enforce the ko rule by walking back up the tree and checking the new
    # state against the whole history
    @property
    def situation(self):
        return (self.next_player, self.board)

    def does_move_violate_ko(self, player, move):
        # If the game is not a play, return False
        if not move.is_play:
            return False
        # Get a new board where the play will be applied
        next_board = copy.deepcopy(self.board)
        # Apply the play and save the 'next' situation
        next_board.place_stone(player, move.point)
        next_situation = (player.other, next_board.zobrist_hash())
        # Check if the hash has already been stored, meaning the game state
        # has already happend and we would be violating the ko rule
        return next_situation in self.previous_states

    # Decide whether a move is valid by using knowledge from both ko and
    # self capture
    def is_valid_move(self, move):
        # If the game is already over return False
        if self.is_over():
            return False
        # For any of these moves, the ko or self-capture can't happen
        if move.is_pass or move.is_resign:
            return True
        return (
            # The point we try to set a stone into is empty
            self.board.get(move.point) is None and
            # Doesn't violate the self capture rule
            not self.is_move_self_capture(self.next_player, move) and
            # Doesn't violate the ko rule
            not self.does_move_violate_ko(self.next_player, move))
