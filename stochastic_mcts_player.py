"""
    根据"A Monte-Carlo AIXI Approximation"略作修改实现的支持stochastic的mcts算法.
    see https://arxiv.org/abs/0909.0801v2
"""


import math
import random
import time
from typing import Union, Dict, Tuple, Set
import numpy as np
import copy
from board import Board as State
from board import Move as Action
from board import *
from operator import itemgetter

C = 1
M = 100
alpha = -1
beta = 1


class Node:
    def __init__(self, parent, is_chance: bool, state: State, action: Action = None):
        assert is_chance == (action is not None)

        self.parent = parent
        self.is_chance = is_chance
        self.state = state

        # chance state only
        self.action = action

        self.children = {}
        self.visits = 0

        self.value = 0

    def generate_children(self):
        if not self.is_chance:
            moves = self.state.all_moves()
            for move in moves:
                self.children[move] = Node(self, True, self.state, move)
        else:
            src, dst = self.action.src, self.action.dst
            if src != dst or self.state.grids[src] != 砖块:
                INVALID_BORN = -1
                self.children[INVALID_BORN] = Node(self, False, self.state.try_move(self.action))
            else:
                for random_born in self.state.bricked:
                    self.children[random_born] = Node(self, False, self.state.try_born(src, random_born))

    def is_chance_node(self):
        return self.is_chance

    def is_decision_node(self):
        return not self.is_chance


def select_action(h: Node, m: int):
    unvisited = [a for a in h.children if h.children[a].visits == 0]
    if len(unvisited) > 0:
        a = random.choice(unvisited)
        return a
    else:
        a = max(h.children, key=lambda a: ((1 - 2 * h.state.turn) * h.children[a].value / (m * (beta - alpha))
                                           + C * math.sqrt(math.log(h.visits) / h.children[a].visits)))
        return a


def winner_2_reward(winner):
    if winner == -1:
        return 0
    elif winner == 0:
        return 1
    else:
        assert winner == 1
        return -1


def rollout(h: Node, m: int):
    for i in range(m):
        is_end, winner = h.state.board_end()
        if is_end:
            break

        a = h.state.random_move()
        h = Node(h, True, h.state.try_move(a), a)
    else:
        is_end, winner = True, -1
    return winner_2_reward(winner)


def sample(h: Node, m: int):
    if m == 0:
        return 0.
    elif h.is_chance_node():
        if len(h.children) == 0:
            h.generate_children()
        random_show_up = random.choice(list(h.children.keys()))
        o, r = h.children[random_show_up], 0
        reward = r + sample(o, m - 1)
    else:
        is_end, winner = h.state.board_end()
        if is_end:
            reward = winner_2_reward(winner)
        elif h.visits == 0:
            if len(h.children) == 0:
                h.generate_children()
            reward = rollout(h, m)
        else:
            a = select_action(h, m)
            reward = sample(h.children[a], m)

    h.value = (1 / (h.visits + 1)) * (reward + h.visits * h.value)
    h.visits += 1
    return reward


def rho_uct(state, m=200, min_sample_cnt=1000, time_limit=3):
    root = Node(None, False, state)
    t0 = time.time()
    sample_cnt = 0
    while True:
        sample(root, m)
        sample_cnt += 1
        t = time.time()
        if sample_cnt >= min_sample_cnt and t >= t0 + time_limit:
            break

    return max(root.children, key=lambda action: (1 - 2 * root.state.turn) * root.children[action].value)


class RhoUCTPlayer:
    def __init__(self, m=200, min_sample_cnt=1000, time_limit=3):
        self.m = m
        self.min_sample_cnt = min_sample_cnt
        self.time_limit = time_limit

    def get_move(self, state):
        print("Player PhoUCT is thinking...")
        return rho_uct(state, self.m, self.min_sample_cnt, self.time_limit)


if __name__ == "__main__":
    s = """
鼠　　　 蓝空空空
　　　　 空空空砖
　象　　 空红空空
　虎　　 空红空空 蓝 {} {象}
        """
    board = Board.from_str(s)

    from game import *
    from human_player import HumanPlayer

    game = Game(player0=RhoUCTPlayer(), player1=HumanPlayer(), init_board=board)
    game.run()
