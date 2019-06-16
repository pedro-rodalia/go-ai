from dlgo.minimax import minimax
from dlgo.ttt.tttboard import GameState, Player, Move
from dlgo.ttt.ttttypes import Point

# Names for the columns
COL_NAMES = 'ABC'

# Function that prints the board based on the current game state
def print_board(board):
    # Print first line
    print('   A   B   C')
    # Fer each row
    for row in (1, 2, 3):
        # Store pieces of this row in a set
        pieces = []
        # For each column
        for col in (1, 2, 3):
            # Get the piece in this position if any
            piece = board.get(Point(row, col))
            # Set a different piece depending on the player that holds this
            # position
            if piece == Player.x:
                pieces.append('X')
            elif piece == Player.o:
                pieces.append('O')
            else:
                pieces.append(' ')
        # Print the row joining positions with '|'
        print('%d  %s' % (row, ' | '.join(pieces)))


# Get point from human input
def point_from_coords(text):
    # The col name is the first character
    col_name = text[0]
    # The row number is the second character
    row = int(text[1])
    # Return point where the col number is defined from the column names set
    return Point(row, COL_NAMES.index(col_name) + 1)


# Main function that runs the program
def main():
    # Create a new game with the GameState instance
    game = GameState.new_game()

    # Declare human players
    human_player = Player.x

    # Declare bots
    bot = minimax.MinimaxAgent()

    # While the game is not over
    while not game.is_over():
        print(chr(27) + "[2J")
        print_board(game.board)
        # If the next player is the human player wait for input
        if game.next_player == human_player:
            # Ask for input for the next move
            human_move = input('-- ')
            # Get point from user input
            point = point_from_coords(human_move.strip())
            # Store move for this point
            move = Move(point)
        else:
            # Tell the bot to select a move
            move = bot.select_move(game)
        # Apply the move
        game = game.apply_move(move)

    # When the game ends
    print(chr(27) + "[2J")
    print_board(game.board)
    # Store the winner
    winner = game.winner()
    # Print out the winner
    if winner is None:
        print("It's a draw.")
    else:
        print('Winner: ' + str(winner))


if __name__ == '__main__':
    main()
