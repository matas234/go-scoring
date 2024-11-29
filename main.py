import time
from typing import List
import numpy as np
import cProfile
import pstats

from delete_timeline_folder import deleteTimeline
from load_game import loadGame

from string_manager import StringManager
from bouzy import Bouzy
from debugger import Debugger




class Score:
    def __init__(self, board, size):
        self.row_length = size
        self.total_length = size * size
        self.board = board.copy()

        self._cardinals_cache = [self.__computeCardinals(i) for i in range(self.total_length)]
        self._neighbor_cache = [self.__computeNeighbors(i) for i in range(self.total_length)]

        self.debugger = Debugger(self)
        self.string_manager = StringManager(self)
        self.bouzy = Bouzy(self)

        self.captures = {-1: 0, 1: 0}


    def __computeCardinals(self, idx: int) -> List[int]:
        cardinals = []

        for offset in [self.row_length, -self.row_length, 1, -1]:
            cardinal = idx + offset
            if (0 <= cardinal < self.total_length and                    # in bounds of the board
                not (offset == -1 and idx % self.row_length == 0) and   #
                not (offset == 1 and (idx + 1) % self.row_length == 0)  # handling edges
            ):
                cardinals.append(cardinal)

        return cardinals


    def __computeNeighbors(self, idx: int) -> List[int]:
        neighbors = []
        rl = self.row_length

        for offset in [rl, -rl, 1, -1, rl+1, rl-1, -rl+1, -rl-1]:
            neigh = idx + offset
            if (0 <= neigh < self.total_length and             # in bounds of the board
                not (offset%rl == 18 and idx % rl == 0) and    #
                not (offset% rl == 1 and (idx + 1) % rl == 0)  # handling edges
            ):
                neighbors.append(neigh)

        return neighbors


    def initialiseAttributes(self) -> None:
        self.bouzy.bouzyAlgorithm(8,21)
        self.string_manager.findStrings()
        self.string_manager.findGroups()
        self.string_manager.generateGroupProperties()
        self.string_manager.calculateStability()


    def scoreBoard(self, history = 1, komi = 6.5, rules = 'japanese', debug = False) -> int:
        self.initialiseAttributes()

        if debug:
            self.debugger.debug(path = "timeline", history = history)

        max_stability = max(group.stability for group in self.string_manager.groups)

        if max_stability == 100:
            white_ter = len(set.union(
                *[group.territory
                if group.nature == -1
                else set()
                for group in self.string_manager.groups]
            ))
            black_ter = len(set.union(
                *[group.territory
                if group.nature == 1
                else set()
                for group in self.string_manager.groups]
            ))

            score = white_ter - black_ter + komi
            if rules == 'japanese':
                score += self.captures[1] - self.captures[-1]
            print(f"SCORE: {'B' if score < 0 else 'W'}+{abs(score)}")

            return score

        groups_to_remove = [group for group in self.string_manager.groups if group.stability == max_stability]
        for group in groups_to_remove:
            for idx in group.stones:
                self.board[idx] = 0
                self.captures[group.nature] += 1

        self.reset()

        return self.scoreBoard(history+1, debug=debug)


    def reset(self) -> None:
        self.bouzy.reset(self.board)
        self.string_manager.reset()





if __name__ == "__main__":
    deleteTimeline()
    board = loadGame("games/snapback.sgf")

    score = Score(board = board, size = int(np.sqrt(board.size)))
    score.scoreBoard(debug=True)
    # cProfile.run('score.initialiseAttributes()', 'assets/profile_data.prof')
    # profiler = cProfile.Profile()
    # profiler.enable()
    # start = time.time()

    # end = time.time()
    # print(f"Took {end-start} seconds")
    # profiler.disable()
    # with open("assets/profile_results.txt", "w") as f:
    #     stats = pstats.Stats(profiler, stream=f)
    #     stats.sort_stats(pstats.SortKey.TIME)
    #     stats.print_stats()
