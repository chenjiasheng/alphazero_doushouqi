import copy
import random
from typing import List, Set
from termcolor import cprint

红鼠 = 0
红猫 = 1
红狗 = 2
红狼 = 3
红豹 = 4
红虎 = 5
红狮 = 6
红象 = 7
蓝鼠 = 8
蓝猫 = 9
蓝狗 = 10
蓝狼 = 11
蓝豹 = 12
蓝虎 = 13
蓝狮 = 14
蓝象 = 15
砖块 = 16
空白 = 17


def distance(src:int, dst:int):
    assert all(x in range(16) for x in [src, dst])
    row1, col1 = src // 4, src % 4
    row2, col2 = dst // 4, dst % 4
    return abs(row1 - row2) + abs(col1 - col2)

def normalize_piece(piece):
    assert 红鼠 <= piece <= 蓝象
    if piece > 红象:
        return piece - 8
    else:
        return piece

def cmp_piece(piece1, piece2):
    assert all(红鼠 <= piece <= 蓝象 for piece in [piece1, piece2])

    piece1, piece2 = normalize_piece(piece1), normalize_piece(piece2)
    if piece1 == piece2:
        return 0

    if piece1 == 红鼠  and piece2 == 红象:
        return 1
    elif piece1 == 红象 and piece2 == 红鼠:
        return -1
    elif piece1 < piece2:
        return -1
    else:
        return 1

class Move:
    def __init__(self, src: int, dst: int):
        self.src = src
        self.dst = dst

    def __repr__(self):
        return "Move(" + str(self.src) + "," + str(self.dst) + ")"

class Board:
    def __init__(self, grids: List[int], bricked: List[int], turn: int):
        assert all(红鼠 <= x <= 空白 for x in grids)
        assert all(红鼠 <= x <= 蓝象 for x in bricked)
        pieces = [x for x in grids if x not in [砖块, 空白]]
        pieces_set = set(pieces)
        assert len(pieces) == len(pieces_set)
        assert len(pieces_set.intersection(bricked)) == 0
        assert grids.count(砖块) == len(bricked)

        self.grids = grids
        self.bricked = bricked
        self.turn = turn

    def normalize_suicide_move(self, move):
        src, dst = move.src, move.dst
        if (self.is_self(src)
                and self.is_oppo(dst)
                and distance(src, dst) == 1
                and cmp_piece(self.grids[src], self.grids[dst]) < 0):
            return Move(src, src)
        else:
            return None

    def is_legal_move(self, move):
        src, dst = move.src, move.dst
        if not all(x in range(16) for x in [src, dst]):
            return False
        if self.grids[src] == 空白:
            return False
        if self.grids[src] == 砖块:
            if src != dst:
                return False
            return True
        src_side = self.grids[src] // 8
        if src_side != self.turn:
            return False

        if src == dst:
            return any(self.grids[x] not in [砖块, 空白]
                       and self.grids[x] // 8 != self.turn
                       and cmp_piece(self.grids[src], self.grids[x]) < 0
                       for x in [src - 1, src + 1, src - 4, dst - 4])

        move_distance = distance(src, dst)
        if move_distance != 1:
            return False
        if self.grids[dst] == 空白:
            return True
        dst_side = self.grids[dst] // 8
        if src_side == dst_side:
            return False
        if cmp_piece(self.grids[src], self.grids[dst]) >= 0:
            return True
        else:
            return False

    def is_of_side(self, index, side):
        return self.grids[index] - side * 8 in range(8)

    def is_self(self, index):
        return self.is_of_side(index, self.turn)

    def is_oppo(self, index):
        return self.is_of_side(index, 1 - self.turn)

    def all_moves(self):
        moves = set()
        for src in range(16):
            if self.grids[src] == 空白:
                continue

            if self.grids[src] == 砖块:
                moves.add(Move(src, src))
                continue

            if not self.is_self(src):
                continue

            dsts = set()
            row, col = src // 4, src % 4
            if row > 0:
                dsts.add(src - 4)
            if row < 3:
                dsts.add(src + 4)
            if col > 0:
                dsts.add(src - 1)
            if col < 3:
                dsts.add(src + 1)

            can_suicide = False
            for dst in dsts:
                if self.is_self(dst) or self.grids[dst] == 砖块:
                    continue
                if self.grids[dst] == 空白:
                    moves.add(Move(src, dst))
                    continue
                cmp = cmp_piece(self.grids[src], self.grids[dst])
                if cmp < 0:
                    can_suicide = True
                    continue
                else:
                    moves.add(Move(src, dst))
                    continue
            if can_suicide:
                moves.add(Move(src, src))
        return moves

    def do_move(self, move):
        # assert self.legal_move(move)
        src, dst = move.src, move.dst
        assert self.grids[src] == 砖块 or self.is_self(src)

        if self.grids[src] == 砖块:
            assert src == dst
            rand = random.randrange(len(self.bricked))
            self.grids[src] = self.bricked[rand]
            del self.bricked[rand]
        elif self.grids[dst] == 空白:
            self.grids[dst], self.grids[src] = self.grids[src], 空白
        elif dst == src:
            self.grids[src] = 空白
        else:
            cmp = cmp_piece(self.grids[src], self.grids[dst])
            assert cmp >= 0
            if cmp == 0:
                self.grids[dst], self.grids[src] = 空白, 空白
            else:
                self.grids[dst], self.grids[src] = self.grids[src], 空白

        self.turn = 1 - self.turn

    def try_move(self, move):
        copy_board = copy.deepcopy(self)
        copy_board.do_move(move)
        return copy_board

    def try_born(self, index, born):
        assert self.grids[index] == 砖块
        assert born in self.bricked
        copy_board = copy.deepcopy(self)
        copy_board.grids[index] = born
        copy_board.bricked.remove(born)
        copy_board.turn = 1 - copy_board.turn
        return copy_board

    def random_move(self):
        moves = self.all_moves()
        return random.choice(list(moves))

    def pieces_of(self, side):
        return {normalize_piece(self.grids[index]): index for index in range(16) if self.is_of_side(index, side)}

    def board_end(self):
        my_pieces = self.pieces_of(self.turn)
        your_pieces = self.pieces_of(1 - self.turn)

        my_bricked = [x for x in self.bricked if x // 8 == self.turn]
        your_bricked = [x for x in self.bricked if x // 8 == 1 - self.turn]

        all_my_pieces = list(my_pieces.keys()) + my_bricked
        all_your_pieces = list(your_pieces.keys()) + your_bricked

        if len(all_my_pieces) == 0 and len(all_your_pieces) != 0:
            return True, 1 - self.turn
        elif len(all_your_pieces) == 0 and len(all_my_pieces) != 0:
            return True, self.turn

        for my_piece in all_my_pieces:
            if all(cmp_piece(my_piece, your_piece) > 0 for your_piece in all_your_pieces):
                return True, self.turn

        for your_piece in all_your_pieces:
            if all(cmp_piece(your_piece, my_piece) > 0 for my_piece in all_my_pieces):
                return True, 1 - self.turn

        if len(my_bricked) == 0 and len(your_bricked) == 0:
            if len(my_pieces) == 1 and len(your_pieces) == 1 and my_pieces.keys() == your_pieces.keys():
                c1 = list(my_pieces.values())[0]
                c2 = list(your_pieces.values())[0]
                dist = distance(c1, c2)
                return True, self.turn if dist % 2 == 1 else 1 - self.turn

        return False, -1

    @staticmethod
    def initial_board():
        return Board([砖块] * 16, list(range(16)), 0)

    def draw(self, verbose=False, indent=0):
        AnimalsStrs = "鼠猫狗狼豹虎狮象"
        def cprint_grid(grid: int, only_color=False, flush=True):
            assert 0 <= grid <= 空白
            if grid == 空白:
                ch = "　" if not only_color else "空"
                cprint(ch, "white", "on_cyan", end="", flush=flush)
            elif grid == 砖块:
                ch = "　" if not only_color else "砖"
                cprint(ch, "white", "on_cyan", attrs=["reverse"], end="", flush=flush)
            elif 0 <= grid <= 16:
                color = 'red' if grid // 8 == 0 else 'blue'
                ch = AnimalsStrs[grid % 8] if not only_color else ("红" if color == "red" else "蓝")
                cprint(ch, color, "on_cyan", end="", flush=flush)
            else:
                assert False

        for row in range(4):
            cprint(" " * indent * 4, end="", flush=True)
            for col in range(4):
                cprint_grid(self.grids[row * 4 + col])
            if verbose:
                print(" ", end="", flush=True)
                for col in range(4):
                    cprint_grid(self.grids[row * 4 + col], only_color=True, flush=True)
            if row != 3:
                print(flush=True)

        ch = "红" if self.turn == 0 else "蓝"
        color = "red" if self.turn == 0 else "blue"
        cprint(" " + ch, color, end=" ", flush=True)

        if verbose:
            cprint("{" + "".join(AnimalsStrs[x] for x in sorted(self.bricked) if x < 8) + "}", "red", end=" ", flush=True)
            cprint("{" + "".join(AnimalsStrs[x - 8] for x in sorted(self.bricked) if x >= 8) + "}", "blue", flush=True)

        return

    @staticmethod
    def from_str(s):
        AnimalsStrs = "鼠猫狗狼豹虎狮象"

        s = s.replace("\r", "").strip("\n").strip(" ").strip("\n").strip(" ")
        lines = s.split("\n")
        assert len(lines) == 4
        assert all(len(line) == 9 and line[4] == " " for line in lines[:3])
        assert len(lines[3]) > 9 and lines[3][4] == " " and lines[3][9] == " "
        grid_lines = lines[:3] + [lines[3][:9]]
        extra_info_line = lines[3][10:]

        animals = "".join([line[:4] for line in grid_lines])
        assert len(animals) == 16 and all(c in AnimalsStrs + "　" for c in animals)
        types = "".join([line[-4:] for line in grid_lines])
        assert len(types) == 16 and all(t in "红蓝砖空" for t in types)

        grids = []
        for i in range(16):
            if types[i] == "空":
                assert animals[i] == "　"
                grids.append(空白)
                continue
            if types[i] == "砖":
                assert animals[i] == "　"
                grids.append(砖块)
                continue
            assert animals[i] != "　"
            grids.append(eval(types[i] + animals[i]))

        turn, red_bricked, blue_bricked = extra_info_line.split(" ")
        turn = 0 if turn == "红" else 1
        red_bricked = [AnimalsStrs.index(c) for c in red_bricked[1:-1]]
        blue_bricked = [AnimalsStrs.index(c) + 8 for c in blue_bricked[1:-1]]
        bricked = red_bricked + blue_bricked
        return Board(grids, bricked, turn)

    def __eq__(self, other):
        return (self.turn == other.turn
                and self.bricked == other.bricked
                and self.grids == other.grids)

    def same_alives_with(self, other):
        if (other.bricked == self.bricked
                and other.pieces_of(0).keys() == self.pieces_of(0).keys()
                and other.pieces_of(1) == self.pieces_of(1)):
            return True
        return False


if __name__ == "__main__":
    s = """
　　　鼠 空空空蓝
　　豹　 空空红砖
　　豹　 空空蓝空
　　　　 空空空空 蓝 {鼠} {}  
    """
    board = Board.from_str(s)
    board.draw(verbose=True)