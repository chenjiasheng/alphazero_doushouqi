import random

Grids = {
    0:  'RE', 1:  'RL', 2:  'RT', 3:  'RP', 4:  'RW', 5:  'RD', 6:  'RC', 7:  'RR',
    8:  'BE', 9:  'BL', 10: 'BT', 11: 'BP', 12: 'BW', 13: 'BD', 14: 'BC', 15: 'BR',
    16: 'ST', 17: 'EM'
}
Animals = "象狮虎豹狼狗猫鼠"

def grid_2_str(grid_id):
    assert isinstance(grid_id, int)
    assert 0 <= grid_id <= 17

    grid = Grids[grid_id]
    assert isinstance(grid, str)
    assert len(grid) == 2
    assert grid in Grids.values()
    if grid[0] == 'R':
        color = 1
        ch = Animals[grid_id]
    elif grid[0] == 'B':
        color = 2
        ch = Animals[grid_id - 8]
    elif grid[0] == 'S':
        color = 3
        ch = '　'
    elif grid[0] == 'E':
        color = 4
        ch = '　'
    else:
        assert False
    return ch, color


class Position:
    def __init__(self, grids, deads):
        assert isinstance(grids, list)
        assert isinstance(deads, list)
        assert len(grids) == 16
        assert all(0 <= x <= 17 for x in grids)
        assert 0 <= len(deads) <= 16
        assert all(0 <= x <= 15 for x in deads)
        assert not any(x in deads for x in grids)
        assert len(deads) == grids.count(17)
        self.grids = grids
        self.deads = deads

    @staticmethod
    def random_position():
        # deads_cnt, stone_cnt, alive_cnt
        alive_cnt = random.randint(0, 16)
        deads_cnt = random.randint(0, 16 - alive_cnt)
        stone_cnt = 16 - alive_cnt - deads_cnt

        pieces = list(range(16))
        random.shuffle(pieces)

        deads = pieces[:deads_cnt]
        alives = pieces[deads_cnt: deads_cnt + alive_cnt]
        stones = [16] * stone_cnt
        emptys = [17] * deads_cnt

        grids = alives + stones + emptys
        random.shuffle(grids)

        return Position(grids, deads)


random_position = Position.random_position()

from curses import wrapper
from curses import curs_set
import curses

def draw_position(position, stdscr):
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
        row, col = i // 4, i % 4 * 2
        row = row * 2 + 1
        col = col * 2 + 2
        ch, color = grid_2_str(position.grids[i])
        stdscr.addstr(row, col, ch, curses.color_pair(color))
    stdscr.refresh()


def main(stdscr):

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)


    # Clear screen
    stdscr.clear()


    draw_position(random_position, stdscr)
    stdscr.getkey()


wrapper(main)

