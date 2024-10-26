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

        self.eyes = set()
        self.potential_eyes = set()
        self.special_eyes = set()
        self.eye_likes = set()
        self.eyes_in_group = set()


    def addStone(self, idx: int) -> None:
        self.stones[idx] = self.nature


    def addLiberty(self, idx: int) -> None:
        self.liberties[idx] = self.nature

    def addEye(self, idx: int) -> None:
        self.eyes.add(idx)

    def addSpecialEye(self, idx: int) -> None:
        self.special_eyes.add(idx)

    def addEyeLike(self, idx: int) -> None:
        self.eye_likes.add(idx)

    def addPotentialEye(self, idx: int) -> None:
        self.potential_eyes.add(idx)

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
         


class Group:
    def __init__(self) -> None:
        self.indices_of_strings = []
        self.eyes = 0
        self.eyes_set = set()
        self.special_eyes = set()
        self.eye_likes = set()
        self.territory = set()
        self.liberties = set()

    def addIndex(self, idx: int) -> None:
        self.indices_of_strings.append(idx)




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

    
    def __computeCardinals(self, indx: int) -> List[int]:
        cardinals = []
        
        for offset in [self.row_length, -self.row_length, 1, -1]:
            cardinal = indx + offset
            if (0 <= cardinal < self.total_length and                       # in bounds of the board
                not (offset == -1 and indx % self.row_length == 0) and   # 
                not (offset == 1 and (indx + 1) % self.row_length == 0)  # handling edges
            ):
                cardinals.append(cardinal)

        return cardinals 
    
    def __computeNeighbors(self, idx: int) -> List[int]:
        neighbors = []
        rl = self.row_length
        
        for offset in [rl, -rl, 1, -1, rl+1, rl-1, -rl+1, -rl-1]:
            neigh = idx + offset
            if (0 <= neigh < self.total_length and                       # in bounds of the board
                not (offset%rl == 18 and idx % rl == 0) and   # 
                not (offset% rl == 1 and (idx + 1) % rl == 0)  # handling edges
            ):
                neighbors.append(neigh)

        return neighbors 
    



class Bouzy:
    def __init__(self, score_istance: Score) -> None:
        self.score = score_istance
        self.nature = score_istance.board.copy()
        self.intensity = 64 * abs(board) 
        self.buffer_nature = np.zeros(self.score.total_length, dtype=int)
        self.buffer_intensity = np.zeros(self.score.total_length, dtype=int)

    def bouzyAlgorithm(self, n, k) -> None:
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
        self.groups: List[Group] = []


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

            current_group = Group()
            queue = deque([(i, self.strings[i].nature)])

            while queue:
                idx, cur_nature = queue.popleft()

                if idx in used_indices:
                    continue  

                current_group.addIndex(idx)
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
    

    def findEyes(self) -> None:
        for idx in range(len(self.strings)):
            string = self.strings[idx]

            for lib_idx in np.nonzero(string.liberties)[0]:
                cardinals = self.score._cardinals_cache[lib_idx]
                neighbors = self.score._neighbor_cache[lib_idx]                
                
                same_string_cardinals = sum(1 for c in cardinals if string.stones[c])

                friendly_neighbors = sum(1 for n in neighbors if (self.score.board[n] == string.nature))
                friendly_cardinals = sum(1 for n in cardinals if (self.score.board[n] == string.nature))

                enemy_neighbors = sum(1 for n in neighbors if (self.score.board[n] == -string.nature))
                enemy_cardinals = sum(1 for n in cardinals if (self.score.board[n] == -string.nature))
                enemy_corners = enemy_neighbors - enemy_cardinals
                

                if same_string_cardinals == len(cardinals):                                                    # think about edges IMPORTANT
                    string.addEye(lib_idx)

                elif enemy_neighbors == 0 and friendly_neighbors >= 6 and friendly_cardinals == 4:
                    string.addEye(lib_idx)

                elif friendly_neighbors == 7 and enemy_neighbors == 0:
                    string.addEye(lib_idx)

                if friendly_neighbors >= 6 and enemy_corners <= 1:
                    string.addSpecialEye(lib_idx)

                elif friendly_neighbors >= 5 and enemy_neighbors == 0:
                    string.addEyeLike(lib_idx)



    def generateGroupProperties(self) -> None:
        for group in self.groups:
            group.eyes_set = set.union(*[self.strings[idx].eyes for idx in group.indices_of_strings])
            group.eyes = len(group.eyes_set)
            group.potential_eyes = set.union(*[self.strings[idx].potential_eyes for idx in group.indices_of_strings])
            group.eye_likes = set.union(*[self.strings[idx].eye_likes for idx in group.indices_of_strings])
            group.special_eyes = set.union(*[self.strings[idx].special_eyes for idx in group.indices_of_strings])

            self.locateContiguousEyesOfGroup(group)

        
    def locateContiguousEyesOfGroup(self, group: Group) -> None:
        visited = set()
        
        def _dfs(idx: int, sequence: list, to_remove: int) -> list:
            visited.add(idx)

            if idx in group.eyes_set:
                to_remove += 1

            sequence.append('E' if idx in group.eye_likes else 'S')

            for neigh in self.score._neighbor_cache[idx]:
                if neigh not in visited and (neigh in group.eye_likes or neigh in group.special_eyes):
                    sequence, to_remove= _dfs(neigh, sequence, to_remove)
            
            return sequence, to_remove

        for idx in group.eye_likes | group.special_eyes:
            if idx not in visited:

                sequence, to_remove = _dfs(idx, [], 0)
                print(sequence)
                
                # Count eyes using a sliding window approach
                i = 0
                eye_count = 0
                while i < len(sequence):
                    if i <= len(sequence) - 2:  
                        if sequence[i:i+2] in [['E', 'S'], ['S', 'E'], ['S', 'S']]:
                            eye_count += 1
                            i += 2 
                            continue
                
                    elif i <= len(sequence) - 3:  
                        if sequence[i:i+3] == ['E', 'E', 'E']:
                            eye_count += 1
                            i += 3
                            continue
                    i += 1

                group.eyes += eye_count - to_remove


                

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
            print(string.eyes)
            for eye in string.eyes:
                to_plot[eye] = string.nature * 100

        sns.heatmap(np.reshape(to_plot, (self.score.row_length, self.score.row_length)), annot=True, cmap="binary", cbar=True, center=0)
        plt.savefig("assets/hstrings.png", dpi=300, bbox_inches='tight')
        

    def printGroups(self) -> None:
        plt.figure(figsize=(8, 6))
        to_plot = np.zeros(self.score.total_length, dtype=int)
        
        for idx, group in enumerate(self.score.string_manager.groups):
            for j in group.indices_of_strings:
                to_plot += (idx + 1) * self.score.string_manager.strings[j].stones

        sns.heatmap(np.reshape(to_plot, (self.score.row_length, self.score.row_length)), annot=True, cmap="coolwarm", cbar=True, center=0)
        plt.savefig("assets/hgroups.png", dpi=300, bbox_inches='tight')  

    def printGroupsText(self) -> None:
        rl = self.score.row_length
        with open("assets/out2.txt", "w", encoding="utf-8") as f:     
            for group in self.score.string_manager.groups:
                out_string = [["⚫"]*rl for _ in range(rl)]

                for idx in group.indices_of_strings:
                    string = self.score.string_manager.strings[idx]
                    for stone in np.nonzero(string.stones)[0]:
                        out_string[stone // rl][stone % rl] = "⚪"

                for line in out_string:
                    f.write("".join(line) + "\n")
                f.write(f"eyes: {group.eyes}\n")  
                f.write(f"special eyes: {group.special_eyes}\n") 
                f.write(f"eye likes: {group.eye_likes}\n") 
                

    def printStringsText(self):
        rl = self.score.row_length
        with open("assets/out.txt", "w", encoding="utf-8") as f:
            for i in range(len(self.score.string_manager.strings)):
                string = self.score.string_manager.strings[i]

                out_string = [["⚫"]*rl for _ in range(rl)]

                for idx in np.nonzero(string.stones)[0]:
                    out_string[idx // rl][idx % rl] = "⚪"


                for idx in np.nonzero(string.liberties)[0]:
                    out_string[idx // rl][idx % rl] = "🟢"

                for eye in string.eyes:
                    out_string[eye // rl][eye % rl] = "🔵"

                for s_eye in string.special_eyes:
                    out_string[s_eye // rl][s_eye % rl] = "🟠"        

                for eye_like in string.eye_likes:
                    out_string[eye_like // rl][eye_like % rl] = "🟡"  



                for line_index in range(rl):
                    f.write(f"{''.join(out_string[line_index])}\n")
                f.write(f"Eyes: {string.eyes}\n")




board = loadGame("games/eyes.sgf")


s = time.time()

potential = Score(board = board, size = int(np.sqrt(board.size)))
potential.bouzy.bouzyAlgorithm(8, 21)
potential.string_manager.findStrings()
potential.string_manager.findGroups()
potential.string_manager.findEyes()
potential.string_manager.generateGroupProperties()

e = time.time()
print(f"Took {e-s} seconds")
print("test")


# potential.debugger.printGroups()
# potential.debugger.printHeatMap()
potential.debugger.printStringsText()
potential.debugger.printGroupsText()