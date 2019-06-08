from dlgo import gotypes
from dlgo.agent.naive import RandomBot
from dlgo import goboard as goboard
from dlgo.utils import print_board, print_move, point_from_coords
import time

def main():

    # Define board size
    board_size = 9
    # Start a new game and store it in the game variable
    game = goboard.GameState.new_game(board_size)
    # Declare the players from the naive bot agent
    bot = RandomBot()

    # Game loop
    while not game.is_over():

        # Before each move, we clear the screen. This way the board is always
        # printed to the same position on the line command
        print(chr(27) + "[2J")
        # Print the board
        print_board(game.board)

        # Tell the bot to select a move
        if game.next_player == gotypes.Player.black:
            human_move = input('-- ')
            point = point_from_coords(human_move.strip())
            move = goboard.Move.play(point)
        else:
            move = bot.select_move(game)

        # Print the next move
        print_move(game.next_player, move)
        # Apply the move
        game = game.apply_move(move)


if __name__ == '__main__':
    main()
