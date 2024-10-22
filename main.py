from collections import defaultdict
import copy
import time
from typing import List, Tuple

board = None
board_size = 18
def initialize_board():
    global board, board_size
    board  = [
            [ 1,  1,  1,  0,  0, -1, -1, -1, -1,  0,  1,  1,  1,  0,  0, -1, -1, -1],
            [ 1,  0,  1,  0,  0, -1,  0, -1, -1,  0,  1,  0,  1,  0,  0, -1,  0, -1],
            [ 1,  1,  1,  0,  0, -1, -1, -1, -1,  0,  1,  1,  1,  0,  0, -1, -1, -1],
            [ 0,  0,  0,  0,  0,  0, -1, -1, -1,  0,  0,  0,  0,  0,  0, -1, -1, -1],
            [-1, -1, -1, -1, -1,  0,  0, -1,  0,  0, -1, -1, -1, -1,  0,  0, -1,  0],
            [-1,  0, -1,  0, -1,  0,  0, -1,  0,  0, -1,  0, -1,  0, -1,  0, -1,  0],
            [-1, -1, -1,  0, -1, -1,  0, -1, -1,  0, -1, -1, -1, -1, -1,  0, -1, -1],
            [ 0,  0,  0,  0,  0, -1,  0, -1,  0,  0,  0,  0,  0,  0, -1,  0, -1,  0],
            [ 1,  1,  0,  0,  0, -1, -1, -1,  0,  0,  1,  1,  0,  0, -1, -1, -1,  0],
            [ 1,  0,  1,  0,  0,  0, -1, -1, -1,  0,  1,  0,  1,  0,  0, -1, -1, -1],
            [ 1,  1,  1,  0,  0,  0, -1, -1,  0,  0,  1,  1,  1,  0,  0, -1, -1,  0],
            [ 0,  0,  0,  0,  0,  0, -1,  0,  0,  0,  0,  0,  0,  0,  0, -1,  0,  0],
            [-1, -1, -1, -1, -1,  0,  0, -1,  0,  0, -1, -1, -1, -1,  0,  0, -1,  0],
            [-1,  0, -1,  0, -1,  0,  0, -1,  0, -1, -1,  0, -1,  0, -1,  0, -1,  0],
            [-1, -1, -1,  0, -1, -1,  0, -1, -1,  0, -1, -1, -1, -1, -1,  0, -1, -1],
            [ 0,  0,  0,  0,  0, -1,  0, -1,  0,  0,  0,  0,  0,  0, -1,  0, -1,  0],
            [ 1,  1,  0,  0,  0, -1, -1, -1,  0,  0,  1,  1,  0,  0, -1, -1, -1,  0],
            [ 1,  0,  1,  0,  0,  0, -1, -1, -1,  0,  1,  0,  1,  0,  0, -1, -1, -1],
        ]


class String:
    def __init__(self):
        self.stones: List[Tuple[int, int]] = []
        self.stonesSet = set()
        self.halfConnections = set()
        self.fullConnections = set()


    def addStone(self, x: int, y: int) -> None:
        self.stonesSet.add((x, y))
        self.stones.append((x,y))


    def generateConnections(self) -> None:
        for (x, y) in self.stones:
            # Full connections
            for dx, dy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
                nx = x + dx
                ny = y + dy

                if (nx >= 0 and nx < board_size and
                    ny >= 0 and ny < board_size and                
                    (nx, ny) not in self.stonesSet and
                    (x, y+dy) not in self.stonesSet and
                    (x+dx, y) not in self.stonesSet
                ):
                    self.fullConnections.add((nx, ny))           
           
            # Half connections
            for dx, dy in [(1,0), (-1, 0), (0, 1), (0, -1)]:
                nx = x + 2*dx
                ny = y + 2*dy

                if (nx >= 0 and nx < board_size and
                    ny >= 0 and ny < board_size and
                    (nx, ny) not in self.stonesSet and
                    (nx, ny) not in self.fullConnections and
                    (x+dx, y+dy) not in self.stonesSet
                ):
                    self.halfConnections.add((nx, ny))


class Score:
    def __init__(self):
        self.strings: List[String] = []
        self.groups: List[List[int]] = []



    def printStrings(self) -> None:
        with open("out.txt", "w", encoding="utf-8") as f:
            for i in range(len(self.strings)):
                string = self.strings[i].stones
                half = self.strings[i].halfConnections
                full = self.strings[i].fullConnections

                out_string = [["⚫"]*board_size for _ in range(board_size)]
                out_con = [["⚫"]*board_size for _ in range(board_size)]

                for (x, y) in string:
                    out_string[x][y] = "⚪"
                    out_con[x][y] = "⚪"

                for (x, y) in half:
                    out_con[x][y] = "🔴"

                for (x, y) in full:
                    out_con[x][y] = "🔵"

                for line_index in range(board_size):
                    f.write(f"{"".join(out_string[line_index])}  {"".join(out_con[line_index])} \n")
                f.write("\n\n")

            for i in range(len(self.groups)):
                out = [["⚫"]*board_size for _ in range(board_size)]

                for index in self.groups[i]:
                    string = self.strings[index].stones
                    for (x, y) in string:
                        out[x][y] = "⚪"                

                for line_index in range(board_size):
                    f.write(f"{"".join(out[line_index])}\n")
                f.write("\n\n")



    def findStrings(self):
        visited = [[False]*board_size for _ in range(board_size)]
        curString = String()

        def _dfs(x: int, y: int) -> None:
            curString.addStone(x, y)
            visited[x][y] = True

            for nx, ny in [(x+1,y), (x-1, y), (x, y+1), (x, y-1)]:
                if (nx >= 0 and nx < board_size 
                    and ny>=0 and ny < board_size 
                    and (not visited[nx][ny]) 
                ):
                    if board[nx][ny] == -1:
                        _dfs(nx, ny)

        for x in range(board_size):
            for y in range(board_size):
                if (board[x][y] == -1
                    and (not visited[x][y])
                ):
                    _dfs(x, y)
                    curString.generateConnections()
                    self.strings.append(curString)
                    curString = String()



    def findGroups(self) -> None:
        used_indices = set()

        for i in range(len(self.strings)):
            if i in used_indices:
                continue  

            current_group = []
            queue = [i]

            while queue:
                idx = queue.pop(0)

                if idx in used_indices:
                    continue  

                current_group.append(idx)
                used_indices.add(idx)

                for j in range(len(self.strings)):
                    if j not in used_indices:
                        occupied_stones = self.strings[idx].stonesSet
                        full_cons = self.strings[j].fullConnections
                        half_cons = self.strings[j].halfConnections

                        if bool(occupied_stones & full_cons) or len(occupied_stones & half_cons) >= 2:
                            queue.append(j)  #

            self.groups.append(current_group)
        

        

start_time = time.time()

for i in range(1):
    initialize_board()
    obj = Score()
    obj.findStrings()
    obj.findGroups()
    obj.printStrings()

end_time = time.time()

print(f"took {end_time - start_time} seconds")

### 🟢🟡🔴