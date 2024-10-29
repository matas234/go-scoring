import numpy as np


class Bouzy:
    def __init__(self, score_istance) -> None:
        self.score = score_istance
        self.nature = score_istance.board.copy()
        self.intensity = 64 * abs(score_istance.board) 
        self.buffer_nature = np.zeros(self.score.total_length, dtype=int)
        self.buffer_intensity = np.zeros(self.score.total_length, dtype=int)
 
    def copyBoardToArrays(self, board) -> None:
        np.copyto(self.nature, board)
        self.intensity = 64 * abs(board)


    def reset(self, board) -> None:
        self.copyBoardToArrays(board)
        self.buffer_nature.fill(0)
        self.buffer_intensity.fill(0)

    def bouzyAlgorithm(self, n, k) -> None:
        for _ in range(n):
            self.__dilateBoard()
        for _ in range(k):
            self.__eraseBoard()


    def __dilateBoard(self) -> None:
        self.__copyToBuffer()        
        for idx in range(self.score.total_length):
            cur_nature = self.buffer_nature[idx]

            for idx_new in self.score._cardinals_cache[idx]:
                if self.buffer_nature[idx_new] and self.buffer_nature[idx_new] != cur_nature:
                    if cur_nature != 0:
                        break
                    else:
                        cur_nature = self.buffer_nature[idx_new]
            else:
                if cur_nature == 0:
                    continue 
                
                self.nature[idx] = cur_nature
                for idx_new in self.score._cardinals_cache[idx]:
                    if self.buffer_nature[idx_new] == cur_nature:
                        self.intensity[idx] += 1
         

    def __eraseBoard(self) -> None:
        self.__copyToBuffer()
        for idx in range(self.score.total_length):
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