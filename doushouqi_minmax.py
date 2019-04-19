import io
import random
import sys
from enum import Enum
from termcolor import colored, cprint

# 0-8 red elephant ~ rat
# 9-15 blue elephat ~ rat
# 16 ~ 23 stoned red elephant ~ rat
# 24 ~ 31 stoned blue elephant ~ rat
# 32 stone
# 33 empty

RED = 0
BLUE = 1
STONED_RED = 2
STONED_BLUE = 3
STONE = 4
EMPTY = 5

EMPTY_GRID = 33
STONED_GRID = 32

UP = 0
DONW = 1
LEFT = 2
RIGHT = 3

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
砖块 = 32
空白 = 33


def type_of_grid(grid):
    if 0 <= grid < 8:
        return RED
    elif 8 <= grid < 16:
        return BLUE
    elif 0 <= grid < 24:
        return STONED_RED
    elif 24 <= grid < 32:
        return STONED_BLUE
    elif grid == STONED_GRID:
        return STONE
    elif grid == EMPTY_GRID:
        return EMPTY
    else:
        assert False

def animal_of_grid(grid):
    assert 0 <= grid < 32
    return grid % 8

def cmp(animal1, animal2):
    assert 0 <= animal1 < 8
    assert 0 <= animal2 < 8
    if animal1 == animal2:
        return 0
    elif animal1 == 0 and animal2 == 7:
        return 1
    elif animal1 == 7 and animal2 == 0:
        return -1
    elif animal1 > animal2:
        return 1
    else:
        return -1

def make_grid(color=None, stoned=None, animal=None):
    if color is None and not stoned:
        assert animal is None
        return 33
    if color is None and stoned:
        assert animal is None
        return 32
    result = animal
    if stoned:
        result += 16
    if color == BLUE:
        result += 8
    return result

def index_2_coord(index):
    assert 0 <= index < 16
    return index // 4, index % 4

def coord_2_index(row, col):
    assert 0 <= row < 4
    assert 0 <= col < 4
    return row * 4 + col

def is_corner(index):
    row, col = index_2_coord(index)
    return row in [0, 3] and col in [0, 3]

def is_edge(index):
    row, col = index_2_coord(index)
    return row in [0, 3] and col in [1, 2] or row in [1, 2] and col in [0, 3]

def is_center(index):
    row, col = index_2_coord(index)
    return row in [1, 2] and col in [1, 2]

def is_neighbour(index1, index2):
    return distance(index1, index2) == 1

def cmp_list(_li1, _li2):
    li1 = sorted(_li1, reverse=True)
    li2 = sorted(_li2, reverse=True)

    li1 = [x % 8 for x in li1]
    li2 = [x % 8 for x in li2]

    if li1 == li2:
        return 0

    return 1 if li1 > li2 else -1


INF_SCORE = 2 ** 9
UNKNOWN = 9999999

class Position:
    def __init__(self, grids, deads, turn):
        assert isinstance(grids, list)
        assert isinstance(deads, list)
        assert len(grids) == 16
        assert all(0 <= x <= 33 for x in grids)
        assert 0 <= len(deads) <= 16
        assert all(0 <= x <= 15 for x in deads)
        assert not any(x in deads for x in grids)
        assert len(deads) == grids.count(33)
        assert turn in [RED, BLUE]
        self.grids = grids
        self.deads = deads
        self.turn = turn

    def copy(self):
        return Position(self.grids.copy(), self.deads.copy(), self.turn)

    def __eq__(self, other):
        return self.turn == other.turn and self.grids == other.grids and self.deads == other.deads

    def type_of_index(self, index):
        return type_of_grid(self.grids[index])

    def type_of_coord(self, row, col):
        return self.type_of_index(coord_2_index(row, col))

    def generate_all_sub_positions(self, random_choice=True):
        assert random_choice
        assert all(0 <= x < 16 or x == EMPTY_GRID or x == STONED_GRID for x in self.grids)
        alives = [x for x in self.grids if 0 <= x < 16]
        stoned = [x for x in list(range(16)) if x not in alives and x not in self.deads]

        all_sub_positions = {}
        for src in range(16):
            row, col = index_2_coord(src)

            type = self.type_of_index(src)
            if type in [1 - self.turn, EMPTY]:
                continue

            if type in [STONED_RED, STONED_BLUE]:
                sub_position = self.copy()
                sub_position.grids[src] = sub_position.grids[src] - 16
                sub_position.turn = 1 - sub_position.turn
                all_sub_positions[(src, None)] = [sub_position]
            elif type == STONE:
                if random_choice:
                    sub_position = self.copy()
                    uncovered = random.choice(stoned)
                    sub_position.grids[src] = uncovered
                    sub_position.turn = 1 - sub_position.turn
                    all_sub_positions[(src, None)] = [sub_position]
                else:
                    assert False
            elif type == self.turn:
                dsts = []
                if row > 0:
                    dsts.append(coord_2_index(row - 1, col))
                if row < 3:
                    dsts.append(coord_2_index(row + 1, col))
                if col > 0:
                    dsts.append(coord_2_index(row, col - 1))
                if col < 3:
                    dsts.append(coord_2_index(row, col + 1))

                for dst in dsts:
                    dst_type = self.type_of_index(dst)
                    if dst_type == EMPTY:
                        sub_position = self.copy()
                        sub_position.grids[dst] = sub_position.grids[src]
                        sub_position.grids[src] = EMPTY_GRID
                        sub_position.turn = 1 - sub_position.turn
                        all_sub_positions[(src, dst)] = [sub_position]
                    elif dst_type == self.turn:
                        continue
                    elif dst_type == 1 - self.turn: # enemy
                        sub_position = self.copy()
                        cmp_result = cmp(animal_of_grid(sub_position.grids[src]), animal_of_grid(sub_position.grids[dst]))
                        if cmp_result == 0:
                            sub_position.deads += [sub_position.grids[src], sub_position.grids[dst]]
                            sub_position.grids[dst] = EMPTY_GRID
                            sub_position.grids[src] = EMPTY_GRID
                            sub_position.turn = 1 - sub_position.turn
                            all_sub_positions[(src, dst)] = [sub_position]
                        elif cmp_result == 1:
                            sub_position.deads += [sub_position.grids[dst]]
                            sub_position.grids[dst] = sub_position.grids[src]
                            sub_position.grids[src] = EMPTY_GRID
                            sub_position.turn = 1 - sub_position.turn
                            all_sub_positions[(src, dst)] = [sub_position]
                        elif cmp_result == -1:
                            sub_position.deads += [sub_position.grids[src]]
                            # sub_position.grids[dst] = sub_position.grids[dst]
                            sub_position.grids[src] = EMPTY_GRID
                            sub_position.turn = 1 - sub_position.turn
                            all_sub_positions[(src, dst)] = [sub_position]
                        else:
                            assert False
                    else:
                        continue

        return all_sub_positions

    def index_of_piece(self, piece):
        assert 0 <= piece < 16
        return self.grids.index(piece)

    def evaluate(self):
        assert all(0 <= x < 16 or x == EMPTY_GRID or x == STONED_GRID for x in self.grids)
        alives = [x for x in self.grids if 0 <= x < 16]
        stoned = [x for x in list(range(16)) if x not in alives and x not in self.deads]

        red_alives = sorted([x for x in alives if x < 8], reverse=True)
        red_stoned = sorted([x for x in stoned if x < 8], reverse=True)
        blue_alives = sorted([x for x in alives if x >= 8], reverse=True)
        blue_stoned = sorted([x for x in stoned if x >= 8], reverse=True)
        deads = set(self.deads)

        assert len(stoned) == 0

        if len(red_alives) == 0:
            return -INF_SCORE
        elif len(blue_alives) == 0:
            return INF_SCORE

        if (红鼠 in deads or 蓝象 in deads) and (蓝鼠 in deads or 红象 in deads):
            if max(red_alives + red_stoned) > max(blue_alives + blue_stoned) % 8:
                return INF_SCORE
            elif max(red_alives + red_stoned) < max(blue_alives + blue_stoned) % 8:
                return -INF_SCORE
            else:
                if len(red_alives) == 1 and cmp_list(red_alives, blue_alives) == 0:
                    dist = distance(self.index_of_piece(red_alives[0]),
                                    self.index_of_piece(blue_alives[0]))
                    if dist % 2 == self.turn:
                        return -INF_SCORE
                    else:
                        return INF_SCORE
                if len(red_alives) == 2 and cmp_list(red_alives, blue_alives) == 0:
                    crd00 = self.index_of_piece(red_alives[0])
                    crd01 = self.index_of_piece(red_alives[1])
                    crd10 = self.index_of_piece(blue_alives[0])
                    crd11 = self.index_of_piece(blue_alives[1])

                    if is_corner(crd01) and is_neighbour(crd01, crd00) and is_neighbour(crd01, crd11):
                        return -INF_SCORE
                    elif is_corner(crd11) and is_neighbour(crd11, crd00) and is_neighbour(crd11, crd10):
                        return INF_SCORE
                    else:

                        dist0 = distance(self.index_of_piece(red_alives[0]),
                                         self.index_of_piece(blue_alives[0]))
                        dist1 = distance(self.index_of_piece(red_alives[1]),
                                         self.index_of_piece(blue_alives[1]))

                        if (dist0 + dist1) % 2 == self.turn:
                            if is_center(crd10) and (self.turn == 1 or not is_neighbour(crd11, crd00)):
                                return -INF_SCORE
                        else:
                            if is_center(crd00) and (self.turn == 0 or not is_neighbour(crd01, crd10)):
                                return INF_SCORE
                if len(red_alives) == 2 and len(blue_alives) == 1 and cmp_list(red_alives, blue_alives) > 0:
                    crd00 = self.index_of_piece(red_alives[0])
                    crd01 = self.index_of_piece(red_alives[1])
                    crd10 = self.index_of_piece(blue_alives[0])
                    if self.turn == RED:
                        return INF_SCORE
                    elif is_neighbour(crd10, crd01) and distance(crd00, crd01) % 2 == 0:
                        return -INF_SCORE
                    else:
                        return INF_SCORE
                if len(blue_alives) == 2 and len(red_alives) == 1 and cmp_list(red_alives, blue_alives) < 0:
                    crd00 = self.index_of_piece(red_alives[0])
                    crd10 = self.index_of_piece(blue_alives[0])
                    crd11 = self.index_of_piece(blue_alives[1])
                    if self.turn == BLUE:
                        return -INF_SCORE
                    elif is_neighbour(crd00, crd11) and distance(crd10, crd11) % 2 == 0:
                        return INF_SCORE
                    else:
                        return -INF_SCORE
        else:
            if 红鼠 in alives and blue_alives == [蓝象]:
                return INF_SCORE
            elif 蓝鼠 in alives and blue_alives == [红象]:
                return -INF_SCORE

        return sum(2 ** x for x in red_alives) - sum(2 ** (x - 8) for x in blue_alives)


    @staticmethod
    def alphabeta(position, depth, alpha, beta, maximizingPlayer, report_move=False):
        score = position.evaluate()
        if depth == 0 or (score and abs(score) == INF_SCORE):
            if report_move:
                return score, None
            else:
                return score
        if maximizingPlayer:
            value = -INF_SCORE
            sub_positions = position.generate_all_sub_positions()

            kill_move = next((move for move in sub_positions if sub_positions[move][0].evaluate() == INF_SCORE), None)
            if kill_move:
                return value if not report_move else (value, (kill_move, sub_positions[kill_move][0]))

            for move in sub_positions:
                draw_position(sub_positions[move][0], None, 7 - depth)
                next_score = Position.alphabeta(sub_positions[move][0], depth - 1, alpha, beta, False)
                value = max(value, next_score)
                if value >= alpha:
                    alpha = value
                    best_move = move
                if alpha >= beta:
                    break # (*β cut-off *)
            return value if not report_move else (value, (best_move, sub_positions[best_move][0]))
        else:
            value = INF_SCORE
            sub_positions = position.generate_all_sub_positions()

            kill_move = next((move for move in sub_positions if sub_positions[move][0].evaluate() == -INF_SCORE), None)
            if kill_move:
                return value if not report_move else (value, (kill_move, sub_positions[kill_move][0]))

            for move in sub_positions:
                draw_position(sub_positions[move][0], None, 7 - depth)
                next_score = Position.alphabeta(sub_positions[move][0], depth - 1, alpha, beta, True)
                value = min(value, next_score)
                beta = min(beta, value)
                if value <= beta:
                    beta = value
                    best_move = move
                if alpha >= beta:
                    break #(*α cut-off *)
            return value if not report_move else (value, (best_move, sub_positions[best_move][0]))

    @staticmethod
    def random_position():
        # deads_cnt, stone_cnt, alive_cnt
        alive_cnt = random.randint(0, 16)
        # deads_cnt = random.randint(0, 16 - alive_cnt)
        deads_cnt = 16 - alive_cnt
        stone_cnt = 16 - alive_cnt - deads_cnt

        pieces = list(range(16))
        random.shufflecmp_piececmp_piece(pieces)

        deads = pieces[:deads_cnt]
        alives = pieces[deads_cnt: deads_cnt + alive_cnt]
        stoned = pieces[deads_cnt + alive_cnt:]
        stones = [32] * stone_cnt
        emptys = [33] * deads_cnt

        grids = alives + stones + emptys
        random.shuffle(grids)

        turn = random.randint(0, 1)

        return Position(grids, deads, turn)

    @staticmethod
    def sample_position():
        grids = [
            空白, 红狮, 红鼠, 空白,
            蓝虎, 空白, 空白, 空白,
            空白, 空白, 空白, 蓝象,
            空白, 空白, 空白, 空白,
        ]

        deads = [x for x in range(16) if x not in grids]
        return Position(grids, deads, RED)


def grid_2_ch_color(grid: int):
    assert 0 <= grid <= 33
    AnimalsStrs = "鼠猫狗狼豹虎狮象"
    if grid == 33:
        color = 1
        ch = '　'
    elif grid == 32:
        color = 2
        ch = '　'
    elif 0 <= grid <= 16:
        color = 3 if grid // 8 == 0 else 4
        ch = AnimalsStrs[grid % 8]
    else:
        color = 5 if (grid - 16) // 8 == 0 else 6
        ch = AnimalsStrs[(grid - 16) % 8]
    return ch, color


def draw_position(position, stdscr, indent=0):
    def cprint_grid(grid: int):
        assert 0 <= grid <= 33
        AnimalsStrs = "鼠猫狗狼豹虎狮象"
        if grid == 33:
            cprint("　", "white", "on_cyan", end="")
        elif grid == 32:
            cprint("　", "white", "on_cyan", attrs=["reverse"], end="")
        elif 0 <= grid <= 16:
            color = 'red' if grid // 8 == 0 else 'blue'
            ch = AnimalsStrs[grid % 8]
            cprint(ch, color, "on_cyan", end="")
        else:
            assert False

    if stdscr is None:
        for i in range(16):
            if i % 4 == 0:
                if i != 0:
                    cprint("")
                cprint(" " * indent * 4, end="")

            cprint_grid(position.grids[i])
        cprint("turn: " + ("red" if position.turn == 0 else "blue") + ", score: " + str(position.evaluate()),
               "red" if position.turn == 0 else "blue")
        return

    import curses
    curses.initscr()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)

    stdscr.clear()
    stdscr.addstr("""\
┌───┬───┬───┬───┐
│ 　│ 　│ 　│ 　│
├───┼───┼───┼───┤
│ 　│ 　│ 　│ 　│
├───┼───┼───┼───┤
│ 　│ 　│ 　│ 　│
├───┼───┼───┼───┤
│ 　│ 　│ 　│ 　│
└───┴───┴───┴───┘
""")
    for i in range(16):
        row, col = index_2_coord(i)
        row = row * 2 + 1
        col = col * 4 + 2
        ch, color = grid_2_ch_color(position.grids[i])
        stdscr.addstr(row, col, ch, curses.color_pair(color))

    stdscr.addstr(9, 0, "轮到" + ("红方" if position.turn == 0 else "蓝方") + "走了")

    stdscr.refresh()


def get_key(stdsrc):
    if stdsrc is None:
        return sys.stdin.read(1)

    return stdsrc.getkey()

def print_info(stdscr, *args, **kwargs):
    if stdscr is None:
        print(*args, **kwargs)
        return

    f = io.StringIO()
    print(*args, **kwargs, file=f)
    s = f.read()
    stdscr.addstr(11, 0, s)


def distance(coord1, coord2):
    def index2coord(index):
        if isinstance(index, tuple):
            return index
        else:
            return index_2_coord(index)
    coord1, coord2 = index2coord(coord1), index2coord(coord2)
    return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])


def main(stdscr):
    position_list = []

    position = Position.sample_position()
    position_list.append(position)
    print("start position:")
    draw_position(position, stdscr)

    for step in range(1):
        _, move_and_pos = Position.alphabeta(position, 6, -INF_SCORE, INF_SCORE, True, True)
        if not move_and_pos:
            break
        position = move_and_pos[1]
        print("position:", step)
        draw_position(position, stdscr)

        if position in position_list:
            break

        position_list.append(position)

    frame = 0
    while True:
        draw_position(position_list[frame], stdscr)
        x = get_key(stdscr)

        if x[0].lower() == 'a\n' or x == "KEY_LEFT":
            frame = max(0, frame - 1)
        elif x == "\n" or x[0].lower() == 'd\n' or x == "KEY_RIGHT":
            frame = min(len(position_list) - 1, frame + 1)
        else:
            break


GUI = False

if GUI:
    from curses import wrapper
    wrapper(main)
else:
    main(None)

