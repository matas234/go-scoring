from collections import deque
import time
from typing import List
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from loadGame import loadGame

class String:
    def __init__(self, total_length: int) -> None:
        self.stones = np.zeros(total_length, dtype=int)
        self.half_connections = np.zeros(total_length, dtype=int)
        self.full_connections = np.zeros(total_length, dtype=int)
        self.nature = 0
        self.liberties = np.zeros(total_length, dtype=int)


    def addStone(self, idx: int) -> None:
        self.stones[idx] = self.nature


    def addLiberty(self, idx: int) -> None:
        self.liberties[idx] = self.nature


    def generateConnectinos(self) -> None:
        row_length = int(np.sqrt(len(self.half_connections)))

        for idx in np.nonzero(self.stones)[0]:
            x = idx // row_length
            y = idx % row_length

            for dx, dy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
                nx = x + dx
                ny = y + dy

                if (0 <= nx < row_length and
                    0 <= ny < row_length and 
                    not self.stones[nx*row_length + ny] and              ####### need to check teh stone is actually empty  IMPORTANT
                    not self.stones[x*row_length + ny] and
                    not self.stones[nx*row_length + y]
                ):
                    self.full_connections[nx*row_length + ny] = self.nature

            for dx, dy in [(1,0), (-1, 0), (0, 1), (0, -1)]:
                nx = x + 2*dx
                ny = y + 2*dy        

                if (0 <= nx < row_length and
                    0 <= ny < row_length and 
                    not self.stones[nx*row_length + ny] and 
                    not self.full_connections[nx*row_length + ny] and
                    not self.stones[(x+dx)*row_length + (y+dy)]
                ):
                    self.half_connections[nx*row_length + ny] = self.nature     
         


class Score:
    def __init__(self, board, size):
        self.row_length = size
        self.total_length = size * size
        self.board = board.copy()

        self._cardinals_cache = [self.__computeCardinals(i) for i in range(self.total_length)]

        self.debugger = Debugger(self)
        self.string_manager = StringManager(self)
        self.bouzy = Bouzy(self)

    
    def __computeCardinals(self, indx: int) -> List[int]:
        out = []
        
        for offset in [self.row_length, -self.row_length, 1, -1]:
            neigh = indx + offset
            if (0 <= neigh < self.total_length and                       # in bounds of the board
                not (offset == -1 and indx % self.row_length == 0) and   # 
                not (offset == 1 and (indx + 1) % self.row_length == 0)  # handling edges
            ):
                out.append(neigh)

        return out 
    

    
    




class Bouzy:
    def __init__(self, score_istance: Score) -> None:
        self.score = score_istance
        self.nature = score_istance.board.copy()
        self.intensity = 64 * abs(board) 
        self.buffer_nature = np.zeros(self.score.total_length, dtype=int)
        self.buffer_intensity = np.zeros(self.score.total_length, dtype=int)

    def bouzy(self, n, k) -> None:
        for _ in range(n):
            self.__dilateBoard()
        for _ in range(k):
            self.__eraseBoard()


    def __dilateBoard(self) -> None:
        self.__copyToBuffer()        
        for idx in range(self.score.total_length):
            self.__dilateIndex(idx)


    def __dilateIndex(self, idx) -> None:
        cur_nature = self.buffer_nature[idx]

        for idx_new in self.score._cardinals_cache[idx]:
            if self.buffer_nature[idx_new] and self.buffer_nature[idx_new] != cur_nature:
                if cur_nature != 0:
                    return
                else:
                    cur_nature = self.buffer_nature[idx_new]

        if cur_nature == 0:
            return 
        
        self.nature[idx] = cur_nature
        for idx_new in self.score._cardinals_cache[idx]:
            if self.buffer_nature[idx_new] == cur_nature:
                self.intensity[idx] += 1


    def __eraseBoard(self) -> None:
        self.__copyToBuffer()
        for idx in range(self.score.total_length):
            self.__eraseIndex(idx)


    def __eraseIndex(self, idx: int) -> None:
        cur_nature = self.buffer_nature[idx]
        if cur_nature == 0:
            return
        
        for idx_new in self.score._cardinals_cache[idx]:
            if self.buffer_nature[idx_new] != cur_nature:
                self.intensity[idx] -= 1

            if (self.intensity[idx] == 0):
                self.nature[idx] = 0
                break      
    
    
    def __copyToBuffer(self) -> None:
        np.copyto(self.buffer_nature, self.nature)
        np.copyto(self.buffer_intensity, self.intensity)


class StringManager:
    def __init__(self, score_istance: Score) -> None:
        self.score = score_istance
        self.strings: List[String] = []
        self.groups = []


    def findStrings(self) -> None:
        visited = [False] * self.score.total_length
        cur_string = String(self.score.total_length)

        def _dfs(idx: int) -> None:
            visited[idx] = True
            cur_string.addStone(idx)

            for idx_new in self.score._cardinals_cache[idx]:
                if (not visited[idx_new]):
                    if self.score.board[idx_new] == cur_string.nature:
                        _dfs(idx_new)
                    else:
                        cur_string.addLiberty(idx_new)

        for idx in range(self.score.total_length):
            if self.score.board[idx] != 0 and not visited[idx]:
                nature = self.score.board[idx]
                cur_string.nature = nature

                _dfs(idx)

                cur_string.generateConnectinos()
                self.strings.append(cur_string)
                cur_string = String(self.score.total_length)


    def findGroups(self) -> None:
        used_indices = set()

        for i in range(len(self.strings)):
            if i in used_indices:
                continue  

            current_group = []
            queue = deque([(i, self.strings[i].nature)])

            while queue:
                idx, cur_nature = queue.popleft()

                if idx in used_indices:
                    continue  

                current_group.append(idx)
                used_indices.add(idx)

                for j in range(len(self.strings)):
                    nature = self.strings[j].nature
                    if j not in used_indices and nature == cur_nature:
                        occupied_stones = self.strings[idx].stones
                        full_cons = self.strings[j].full_connections
                        half_cons = self.strings[j].half_connections

                        if (np.sum((occupied_stones != 0) & (full_cons != 0)) or 
                            np.sum((occupied_stones != 0) & (half_cons != 0)) >= 2
                        ):
                            queue.append((j, nature))

            self.groups.append(current_group)    
    

class Debugger:
    def __init__(self, score_instance: Score) -> None:
        self.score = score_instance

    def printHeatMap(self) -> None:
            plt.figure(figsize=(8, 6))
            terr = (self.score.bouzy.intensity * self.score.bouzy.nature)
            map = np.where(self.score.board == 0, terr, board*64)
            sns.heatmap(np.reshape(map, (self.score.row_length, self.score.row_length)), annot=True, cmap="coolwarm", cbar=True, center=0)
            plt.savefig("assets/heatmap.png", dpi=300, bbox_inches='tight')


    def printStrings(self) -> None:
        plt.figure(figsize=(8, 6))
        to_plot = np.zeros(self.score.total_length, dtype=int)
        for idx, string in enumerate(self.score.string_manager.strings):
            stones = string.stones * (idx + 1)

            to_plot += stones 

        sns.heatmap(np.reshape(to_plot, (self.score.row_length, self.score.row_length)), annot=True, cmap="binary", cbar=True, center=0)
        plt.savefig("assets/hstrings.png", dpi=300, bbox_inches='tight')
        

    def printGroups(self) -> None:
        plt.figure(figsize=(8, 6))
        to_plot = np.zeros(self.score.total_length, dtype=int)
        
        for idx, group in enumerate(self.score.string_manager.groups):
            for j in group:
                to_plot += (idx + 1) * self.score.string_manager.strings[j].stones

        sns.heatmap(np.reshape(to_plot, (self.score.row_length, self.score.row_length)), annot=True, cmap="coolwarm", cbar=True, center=0)
        plt.savefig("assets/hgroups.png", dpi=300, bbox_inches='tight')       



board = loadGame("games/game1.sgf")
potential = Score(board = board, size = int(np.sqrt(board.size)))



s = time.time()

potential.bouzy.bouzy(8, 21)
potential.string_manager.findStrings()
potential.string_manager.findGroups()

e = time.time()
print(f"Took {e-s} seconds")


potential.debugger.printGroups()
potential.debugger.printHeatMap()
potential.debugger.printStrings()