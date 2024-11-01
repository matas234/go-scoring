import time
from typing import List
import numpy as np
import cProfile
import pstats

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

    
    def scoreBoard(self, history = 1) -> int:
        self.initialiseAttributes()
        self.debugger.debug(path = "timeline", history = history)

        max_stability = max(group.stability for group in self.string_manager.groups)

        if max_stability == 100:
            print("no groups to remove")
            return 0
        
        groups_to_remove = [group for group in self.string_manager.groups if group.stability == max_stability]
        for group in groups_to_remove:
            for idx in group.stones:
                self.board[idx] = 0

        self.reset()
     
        return self.scoreBoard(history+1)


    def reset(self) -> None:
        self.bouzy.reset(self.board)
        self.string_manager.reset()





if __name__ == "__main__":
    with open("timeline/board.txt", "w") as file:
        pass
    board = loadGame("games/game5.sgf")

    score = Score(board = board, size = int(np.sqrt(board.size)))
    score.scoreBoard()
    score.initialiseAttributes()
    score.debugger.debug()

    # cProfile.run('score.initialiseAttributes()', 'assets/profile_data.prof')
    # profiler = cProfile.Profile()
    # profiler.enable()
    # s = time.time()
    # for i in range(0):
    #     score.initialiseAttributes()
    #     score.reset()
    
    # e = time.time()
    # profiler.disable()
    # print(f"Took {e-s} seconds")
    # with open("assets/profile_results.txt", "w") as f:
    #     stats = pstats.Stats(profiler, stream=f)
    #     stats.sort_stats(pstats.SortKey.TIME)
    #     stats.print_stats()
