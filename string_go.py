class String:
    def __init__(self) -> None:
        self.stones = set()
        self.half_connections = set()
        self.full_connections = set()
        self.nature = 0
        self.liberties = set()

        self.eyes = set()
        self.special_eyes = set()
        self.eye_likes = set()
        self.eyes_in_group = set()


    def addStone(self, idx: int) -> None:
        self.stones.add(idx)

    def addLiberty(self, idx: int) -> None:
        self.liberties.add(idx)

    def addEye(self, idx: int) -> None:
        self.eyes.add(idx)

    def addSpecialEye(self, idx: int) -> None:
        self.special_eyes.add(idx)

    def addEyeLike(self, idx: int) -> None:
        self.eye_likes.add(idx)



    def generateConnectinos(self, row_length: int, board) -> None:
        for idx in self.stones:
            x = idx // row_length
            y = idx % row_length

            for dx, dy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
                nx = x + dx
                ny = y + dy

                if (0 <= nx < row_length and
                    0 <= ny < row_length and 
                    nx*row_length + ny not in self.stones and             
                    x*row_length + ny not in self.stones and
                    nx*row_length + y not in self.stones and 
                    (board[nx*row_length + y] == 0 and              ######HERE
                    board[x*row_length + ny] == 0) 

                ):
                    self.full_connections.add(nx*row_length + ny)

            for dx, dy in [(1,0), (-1, 0), (0, 1), (0, -1)]:
                nx = x + 2*dx
                ny = y + 2*dy        

                if (0 <= nx < row_length and
                    0 <= ny < row_length and 
                    nx*row_length + ny not in self.stones and 
                    nx*row_length + ny not in self.full_connections and
                    board[(x+dx)*row_length + y] == 0 and 
                    (x+dx)*row_length + (y+dy) not in self.stones
                ):
                    self.half_connections.add(nx*row_length + ny)     
                