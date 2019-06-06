from dlgo.gotypes import Player
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
    def pass(cls):
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

    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = set(stones)
        self.liberties = set(liberties)

    # Removes a liberty from the string
    def remove_liberty(self, point):
        self.liberties.remove(point)

    # Adds a liberty to the string
    def add_liberty(self, point):
        self.liberties.add(point)

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
        self.grid = {}

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
        # Reduce liberties of any adjacent strings of the opposite color
        for other_color_string in adjaceent_opposite_color:
            other_color_string.remove_liberty(point)
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

    # We have to keep in mind that other stones might gain liberties when
    # removing an enemy string
    def _remove_string(self, string):
        # For each point which belonged to the string
        for point in strings.stones:
            # For each neighbour of this point
            for neighbour in point.neighbours():
                # Get the string that contains this neighbour
                neighbour_string = self._grid.get(neighbour)
                # If neighbour contains no stones skip a loop
                if neighbour_string is None:
                    continue
                # If is not the same string we are checking
                if neighbour_string is not string:
                    # add the point as a liberty
                    neighbour_string.add_liberty(point)
            # Clear the point within the grid
            self._grid[point] = None
