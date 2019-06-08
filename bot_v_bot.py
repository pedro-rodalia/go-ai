from dlgo import gotypes
from dlgo import agent
from dlgo import goboard_slow
from dlgo.utils import print_board, print_move
import time

def main():

    # Define board size
    board_size = 9
    # Start a new game and store it in the game variable
    game = goboard.GameState.new_game(board_size)
    # Declare the players from the naive bot agent
    bots = {
        gotypes.Player.black: agent.naive.RandomBot(),
        gotypes.Player.white: agent.naive.RandomBot()
    }

    # We set a sleep timer to 0.3 seconds so that bot moves aren't printed too
    # fast to observe
    while not game.is_over():
        time.sleep(0.3)

    # Before each move, we clear the screen. This way the board is always
    # printed to the same position on the line command
    print(chr(27) + "[2J]")
    # Print the board
    print_board(game.board)
    # Tell the bot to select a move
    bot_move = bots[game.next_player].select_move(game)
    # Print the next move
    print_move(game.next_player, bot_move)
    # Apply the move
    game = game.apply_move(bot_move)


if __name__ == '__main__':
    main()
