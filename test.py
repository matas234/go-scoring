import time
from typing import List
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from loadGame import loadGame

class Potential:
    def __init__(self, board, size):
        self.row_length = size
        self.total_length = size * size
        self.nature = board.copy()
        self.intensity = 64 * abs(board) 
        self.buffer_nature = np.zeros(self.total_length, dtype=int)
        self.buffer_intensity = np.zeros(self.total_length, dtype=int)

        self.__neighbors_cache = [self.__computeNeighbours(i) for i in range(self.total_length)]


    def printHeatMap(self, board) -> None:
        plt.figure(figsize=(8, 6))
        terr = (self.intensity * self.nature)
        map = np.where(board == 0, terr, board*64)
        sns.heatmap(np.reshape(map, (self.row_length, self.row_length)), annot=True, cmap="coolwarm", cbar=True, center=0)
        plt.savefig("heatmap.png", dpi=300, bbox_inches='tight')

    
    def Bouzy(self, n, k) -> None:
        for _ in range(n):
            self.dilateBoard()
        for _ in range(k):
            self.eraseBoard()
        del self.__neighbors_cache


    def dilateBoard(self) -> None:
        self.__copyToBuffer()        
        for idx in range(self.total_length):
            self.dilateIndex(idx)


    def dilateIndex(self, idx) -> None:
        cur_nature = self.buffer_nature[idx]

        for idx_new in self.__neighbors_cache[idx]:
            if self.buffer_nature[idx_new] and self.buffer_nature[idx_new] != cur_nature:
                if cur_nature != 0:
                    return
                else:
                    cur_nature = self.buffer_nature[idx_new]

        if cur_nature == 0:
            return 
        
        self.nature[idx] = cur_nature
        for idx_new in self.__neighbors_cache[idx]:
            if self.buffer_nature[idx_new] == cur_nature:
                self.intensity[idx] += 1


    def eraseBoard(self) -> None:
        self.__copyToBuffer()
        for idx in range(self.total_length):
            self.eraseIndex(idx)


    def eraseIndex(self, idx: int) -> None:
        cur_nature = self.buffer_nature[idx]
        if cur_nature == 0:
            return
        
        for idx_new in self.__neighbors_cache[idx]:
            if self.buffer_nature[idx_new] != cur_nature:
                self.intensity[idx] -= 1

            if (self.intensity[idx] == 0):
                self.nature[idx] = 0
                break      


    def __computeNeighbours(self, indx: int) -> List[int]:
        out = []
        
        for offset in [self.row_length, -self.row_length, 1, -1]:
            neigh = indx + offset
            if (0 <= neigh < self.total_length and                       # in bounds of the board
                not (offset == -1 and indx % self.row_length == 0) and   # 
                not (offset == 1 and (indx + 1) % self.row_length == 0)  # handling edges
            ):
                out.append(neigh)

        return out 
    
    
    def __copyToBuffer(self) -> None:
        np.copyto(self.buffer_nature, self.nature)
        np.copyto(self.buffer_intensity, self.intensity)





board = loadGame("games/game3.sgf")

	
potential = Potential(board = board, size = int(np.sqrt(board.size)))
# print(len(board))
# print(np.reshape(potential.nature, (19, 19)))


s = time.time()
potential.bouzy(8, 21)
e = time.time()
print(f"Took {e-s} seconds")


potential.printHeatMap(board)
