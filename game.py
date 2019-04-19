import copy

from board import *

class Game:
    def __init__(self, player0, player1, init_board=Board.initial_board()):
        self.players = [player0, player1]
        self.board = init_board
        self.history = [copy.deepcopy(self.board)]

    def game_end(self):
        assert self.board == self.history[-1]
        if len(self.history) >= 3 and self.board == self.history[-3]:
            return True, -1
        if (len(self.history) >= 20 and self.board.same_alives_with(self.history[-20])): # todo
            return True, -1
        return self.board.board_end()

    def run(self):
        self.board.draw(True)
        while True:
            is_end, winner = self.game_end()
            if is_end:
                break
            move = self.players[self.board.turn].get_move(self.board)
            self.board.do_move(move)
            self.board.draw(True)
            self.history.append(copy.deepcopy(self.board))
        assert is_end
        if winner == -1:
            print("Draw.")
        else:
            print("Player %d wins." % winner)


if __name__ == "__main__":
    from human_player import HumanPlayer
    game = Game(player0=HumanPlayer(), player1=HumanPlayer())
    game.run()