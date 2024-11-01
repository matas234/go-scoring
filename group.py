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
        self.double_liberties = set()
        self.half_liberties = set()
        self.third_liberties = set()

        self.stability = -1

        self.stones = set()


    def addIndex(self, idx: int) -> None:
        self.indices_of_strings.append(idx)


    def setAsStable(self) -> None:
        self.stability = 100


    def computeStability(self) -> None:
        if self.stability != -1:
            return

        extra_libs = len(self.half_liberties)/2 + len(self.third_liberties)/3 + len(self.double_liberties)

        if self.eyes >= 2:
            self.stability = 100

        elif (self.eyes == 1 and
              len(self.special_eyes) + len(self.eye_likes) >= 2 and   ##### HAVE TO BE NOT CONTIGOUS IMPORTANT
              len(self.territory) >= 3
              ):
            self.stability = 100

        elif (self.eyes == 0 and
              len(self.territory) >= 6
              ):
            self.stability = 100

        else:
            self.stability = round(520 - (self.eyes / 2) - (len(self.liberties) + extra_libs) / 2 - (len(self.territory) / 2))

