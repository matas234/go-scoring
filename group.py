import numpy as np

class Group:
    def __init__(self) -> None:
        self.indices_of_strings = []
        self.nature = 0

        self.eyes = 0
        self.eyes_set = set()
        self.special_eyes = set()
        self.eye_likes = set()

        self.territory = set()
        self.liberties = set()
        self.stability = -1

        self.stones = np.array


    def addIndex(self, idx: int) -> None:
        self.indices_of_strings.append(idx)


    def setAsStable(self) -> None:
        self.stability = 100


    def computeStability(self) -> None:
        if self.territory != -1:
            raise RuntimeError("Stability is being recalculateted (shouldnt be happening)") 


        if self.eyes >= 2:
            self.stability = 100

        elif (self.eyes == 1 and
              len(self.special_eyes) + self.eye_likes >= 2 and   ##### HAVE TO BE NOT CONTIGOUS IMPORTANT
              self.territory >= 3
              ):
            self.stability = 100

        elif (self.eyes == 0 and
              self.territory >= 6
              ):
            self.stability = 100

        else:
            self.stability = 520 - (self.eyes / 2) - (self.liberties * 2) - (self.territory / 2)