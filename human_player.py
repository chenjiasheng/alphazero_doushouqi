from board import *

class HumanPlayer:
    def __init__(self):
        pass

    def get_move(self, board: Board):
        s = ""
        while s == "":
            try:
                s = input("your move:")
                src, dst = s.strip().split()
                src, dst = int(src), int(dst)
                move = Move(src, dst)
                if board.is_legal_move(move):
                    break
                else:
                    move = board.normalize_suicide_move(move)
                    if move:
                        break

                s = ""
                print("invalid move.")
                continue

            except:
                s = ""
                print("invalid move.")
                continue

        return move



