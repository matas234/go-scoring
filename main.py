from collections import deque
from functools import reduce
import time
from typing import List
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
import seaborn as sns
from loadGame import loadGame

import cProfile
import pstats

class String:
    def __init__(self) -> None:
        self.stones = set()
        self.half_connections = set()
        self.full_connections = set()
        self.nature = 0
        self.liberties = set()

        self.eyes = set()
        self.potential_eyes = set()
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

    def addPotentialEye(self, idx: int) -> None:
        self.potential_eyes.add(idx)


    def generateConnectinos(self, row_length: int) -> None:
        for idx in self.stones:
            x = idx // row_length
            y = idx % row_length

            for dx, dy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
                nx = x + dx
                ny = y + dy

                if (0 <= nx < row_length and
                    0 <= ny < row_length and 
                    nx*row_length + ny not in self.stones and              ####### need to check teh stone is actually empty  IMPORTANT
                    x*row_length + ny not in self.stones and
                    nx*row_length + y not in self.stones
                ):
                    self.full_connections.add(nx*row_length + ny)

            for dx, dy in [(1,0), (-1, 0), (0, 1), (0, -1)]:
                nx = x + 2*dx
                ny = y + 2*dy        

                if (0 <= nx < row_length and
                    0 <= ny < row_length and 
                    nx*row_length + ny not in self.stones and 
                    nx*row_length + ny not in self.full_connections and
                    (x+dx)*row_length + (y+dy) not in self.stones
                ):
                    self.half_connections.add(nx*row_length + ny)     
                
         


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


    def computeStability(self) -> None:
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
            if (0 <= cardinal < self.total_length and                    # in bounds of the board
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
        self.string_manager.countTerritory()
        self.string_manager.findEyes()
        self.string_manager.generateGroupProperties()


    def reset(self) -> None:
        self.bouzy.reset(self.board)
        self.string_manager.reset()
    


class Bouzy:
    def __init__(self, score_istance: Score) -> None:
        self.score = score_istance
        self.nature = score_istance.board.copy()
        self.intensity = 64 * abs(board) 
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




class StringManager:
    def __init__(self, score_istance: Score) -> None:
        self.score = score_istance
        self.strings: List[String] = []
        self.groups: List[Group] = []


    def findStrings(self) -> None:
        visited = [False] * self.score.total_length
        cur_string = String()

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

                cur_string.generateConnectinos(self.score.row_length)
                self.strings.append(cur_string)
                cur_string = String()


    def findGroups(self) -> None:
        n = len(self.strings)

        used_indices = [False]*n

        for i in range(n):
            if used_indices[i]:
                continue  

            current_group = Group()
            queue = deque([(i, self.strings[i].nature)])

            while queue:
                idx, cur_nature = queue.popleft()

                current_group.addIndex(idx)
                used_indices[idx] = True
                occupied_stones = self.strings[idx].stones

                for j in range(len(self.strings)):
                    nature = self.strings[j].nature
                    if not used_indices[j] and nature == cur_nature:
                        full_cons = self.strings[j].full_connections
                        half_cons = self.strings[j].half_connections

                        if (occupied_stones & full_cons or 
                            len((occupied_stones & half_cons)) >= 2
                        ):
                            used_indices[j] = True
                            queue.append((j, nature))

            self.groups.append(current_group)    
    

    def findEyes(self) -> None:
        for idx in range(len(self.strings)):
            string = self.strings[idx]

            for lib_idx in string.liberties:
                neighbors = self.score._neighbor_cache[lib_idx]
                cardinals = self.score._cardinals_cache[lib_idx]

                same_string_cardinals = 0
                friendly_neighbors = 0
                friendly_cardinals = 0
                enemy_neighbors = 0
                enemy_cardinals = 0

                for c in cardinals:
                    if c in string.stones:
                        same_string_cardinals += 1
                    if self.score.board[c] == string.nature:
                        friendly_cardinals += 1
                    elif self.score.board[c] == -string.nature:
                        enemy_cardinals += 1
                for n in neighbors:
                    if self.score.board[n] == string.nature:
                        friendly_neighbors += 1
                    elif self.score.board[n] == -string.nature:
                        enemy_neighbors += 1
                enemy_corners = enemy_neighbors - enemy_cardinals


                
                if same_string_cardinals == len(cardinals):    
                    string.addEye(lib_idx)

                elif len(cardinals) == 4:    #middle of the board
                    if enemy_neighbors == 0:
                        if friendly_neighbors >= 6 and friendly_cardinals == 4:
                            string.addEye(lib_idx)

                        elif friendly_neighbors == 7:
                            string.addEye(lib_idx)

                    if friendly_neighbors >= 6 and enemy_corners <= 1:
                        string.addSpecialEye(lib_idx)

                    elif friendly_neighbors >= 5 and enemy_neighbors == 0:
                        string.addEyeLike(lib_idx)

                elif len(cardinals) == 3:  # edge of the board
                    if enemy_neighbors == 0:
                        if friendly_neighbors >= 4:
                            string.addSpecialEye(lib_idx)

                        elif friendly_cardinals >= 3:
                            string.addEyeLike(lib_idx)
                    

    def generateGroupProperties(self) -> None:
        for group_idx in range(len(self.groups)):
            group = self.groups[group_idx]

            group.eyes_set = set.union(*[self.strings[idx].eyes for idx in group.indices_of_strings])
            group.eyes = len(group.eyes_set)
            group.potential_eyes = set.union(*[self.strings[idx].potential_eyes for idx in group.indices_of_strings])
            group.eye_likes = set.union(*[self.strings[idx].eye_likes for idx in group.indices_of_strings])
            group.special_eyes = set.union(*[self.strings[idx].special_eyes for idx in group.indices_of_strings])

            group.liberties = set.union(*[set(self.strings[idx].liberties) for idx in group.indices_of_strings])
            group.stones = set.union(*[set(self.strings[idx].stones) for idx in group.indices_of_strings])

            group.nature = self.strings[group.indices_of_strings[0]].nature

            self.locateContiguousEyesOfGroup(group_idx)
            # self.countTerritory(group_idx)

        
    def locateContiguousEyesOfGroup(self, group_idx: int) -> None:
        visited = set()
        group = self.groups[group_idx]
        
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
                if eye_count > 0:
                    group.eyes += eye_count - to_remove


    def reset(self) -> None:
        self.strings = []
        self.groups = []


    def countTerritory(self) -> None:
        ##instance of nature reshaped to be 2d matrix
        nature = self.score.bouzy.nature.reshape(self.score.row_length, self.score.row_length)

        labeled_b_ter, num_b_ters = ndimage.label(nature > 0)
        labeled_w_ter, nums_w_ters = ndimage.label(nature < 0)

        labeled_b_ter = labeled_b_ter.ravel()
        labeled_w_ter = labeled_w_ter.ravel()

        white_regions_sets = [set() for _ in range(nums_w_ters)]
        black_regions_sets = [set() for _ in range(num_b_ters)]


        for idx in range(self.score.total_length):
            if self.score.bouzy.nature[idx] > 0:
                black_regions_sets[labeled_b_ter[idx] - 1].add(idx)
            elif self.score.bouzy.nature[idx] < 0:
                white_regions_sets[labeled_w_ter[idx] - 1].add(idx)

        self.score.debugger.printTerritoryGroups(white_regions_sets, black_regions_sets)

        for group in self.groups:
            if group.nature == -1:
                group.territory = set.union(
                    *[white_regions_sets[idx] - group.stones 
                    if (white_regions_sets[idx] & group.stones)
                    else set() 
                    for idx in range(nums_w_ters)]
                )
            elif group.nature == 1:
                group.territory = set.union(
                    *[(black_regions_sets[idx] - group.stones) 
                    if (black_regions_sets[idx] & group.stones)
                    else set()
                    for idx in range(num_b_ters)]
                )

        ## re-flatten nature once done (might not be necessary)
        self.score.bouzy.nature.ravel()






        


    

class Debugger:
    def __init__(self, score_instance: Score) -> None:
        self.score = score_instance

    def printHeatMap(self) -> None:
        plt.figure(figsize=(8, 6))
        map = (self.score.bouzy.intensity) * self.score.bouzy.nature
        sns.heatmap(np.reshape(map, (self.score.row_length, self.score.row_length)), annot=True, cmap="coolwarm", cbar=True, center=0)
        plt.savefig("assets/heatmap2.png", dpi=300, bbox_inches='tight')



    def printStrings(self) -> None:
        plt.figure(figsize=(8, 6))
        to_plot = np.zeros(self.score.total_length, dtype=int)
        
        for idx, string in enumerate(self.score.string_manager.strings):
            stones = string.stones * (idx + 1)
            to_plot += stones 
            for eye in string.eyes:
                to_plot[eye] = string.nature * 100

        sns.heatmap(np.reshape(to_plot, (self.score.row_length, self.score.row_length)), annot=True, cmap="binary", cbar=True, center=0)
        plt.savefig("assets/hstrings.png", dpi=300, bbox_inches='tight')
        

    def printGroups(self) -> None:
        plt.figure(figsize=(8, 6))
        to_plot = np.zeros(self.score.total_length, dtype=int)
        
        for idx, group in enumerate(self.score.string_manager.groups):
            for j in group.indices_of_strings:
                to_plot[list(self.score.string_manager.strings[j].stones)] = idx + 1

        sns.heatmap(np.reshape(to_plot, (self.score.row_length, self.score.row_length)), annot=True, cmap="coolwarm", cbar=True, center=0)
        plt.savefig("assets/hgroups.png", dpi=300, bbox_inches='tight')  

    def printGroupsText(self) -> None:
        rl = self.score.row_length
        with open("assets/out2.txt", "w", encoding="utf-8") as f:     
            for group in self.score.string_manager.groups:
                out_libs = [["🟤"]*rl for _ in range(rl)]
                out_ter = [["🟤"]*rl for _ in range(rl)]

                for idx in group.liberties:
                    out_libs[idx // rl][idx % rl] = "🟢"

                for idx in group.stones:
                    out_libs[idx // rl][idx % rl] = "⚪" if group.nature == -1 else "⚫"
                    out_ter[idx // rl][idx % rl] = "⚪" if group.nature == -1 else "⚫"

                for idx in group.territory:
                    out_ter[idx // rl][idx % rl] = "🔵"

                for line_index in range(rl):
                    f.write(f"{"".join(out_libs[line_index])}   {"".join(out_ter[line_index])}  \n")

                f.write(f"eyes: {group.eyes}\n")  
                f.write(f"special eyes: {group.special_eyes}\n") 
                f.write(f"eye likes: {group.eye_likes}\n") 
                f.write(f"territory: {len(group.territory)}\n")


    def printTerritoryGroups(self, white_regions_sets, black_regions_sets) -> None:
        rl = self.score.row_length
        with open("assets/out_territory.txt", "w", encoding="utf-8") as f:
            for white_set in white_regions_sets:
                out_ter = [["🟤"]*rl for _ in range(rl)]
                for idx in white_set:
                    out_ter[idx // rl][idx % rl] = "⚪"
                for line in out_ter:
                    f.write(f"{"".join(line)}   \n")
               
                f.write(f"w territory: {white_set}\n")
            for black_set in black_regions_sets:
                out_ter = [["🟤"]*rl for _ in range(rl)]
                for idx in black_set:
                    out_ter[idx // rl][idx % rl] = "⚫"
                for line in out_ter:
                    f.write(f"{"".join(line)}   \n")
                f.write(f"b territory: {black_set}\n")

    def printStringsText(self):
        rl = self.score.row_length
        with open("assets/out.txt", "w", encoding="utf-8") as f:
            f.write(f"🟢 for liberties \n")
            f.write(f"🔵 for eyes \n")
            f.write(f"🟠 for special eyes \n")
            f.write(f"🔴 for eye likes \n")
            for i in range(len(self.score.string_manager.strings)):
                string = self.score.string_manager.strings[i]

                out_libs = [["🟤"]*rl for _ in range(rl)]
                out_eyes = [["🟤"]*rl for _ in range(rl)]
                out_special_eyes = [["🟤"]*rl for _ in range(rl)]
                out_eye_likes = [["🟤"]*rl for _ in range(rl)]

                for idx in string.stones:
                    out_libs[idx // rl][idx % rl] = "⚪" if string.nature == -1 else "⚫"
                    out_eyes[idx // rl][idx % rl] = "⚪" if string.nature == -1 else "⚫"
                    out_special_eyes[idx // rl][idx % rl] = "⚪" if string.nature == -1 else "⚫"
                    out_eye_likes[idx // rl][idx % rl] = "⚪" if string.nature == -1 else "⚫"


                for idx in string.liberties:
                    out_libs[idx // rl][idx % rl] = "🟢"

                for eye in string.eyes:
                    out_eyes[eye // rl][eye % rl] = "🔵"

                for s_eye in string.special_eyes:
                    out_special_eyes[s_eye // rl][s_eye % rl] = "🟠"        

                for eye_like in string.eye_likes:
                    out_eye_likes[eye_like // rl][eye_like % rl] = "🔴"  

                for line_index in range(rl):
                    f.write(f"{''.join(out_libs[line_index])}   {''.join(out_eyes[line_index])}   {''.join(out_special_eyes[line_index])}   {''.join(out_eye_likes[line_index])} \n")
                f.write(f"Eyes: {string.eyes}\n")


########################################################################################################


if __name__ == "__main__":
    board = loadGame("games/game4.sgf")


    potential = Score(board = board, size = int(np.sqrt(board.size)))
    cProfile.run('potential.initialiseAttributes()', 'assets/profile_data.prof')

    profiler = cProfile.Profile()
    profiler.enable()
    s = time.time()
    for i in range(100):
        potential.initialiseAttributes()
        potential.reset()
    
    e = time.time()

    profiler.disable()
    potential.initialiseAttributes()
    print(f"Took {e-s} seconds")
 

    potential.string_manager.countTerritory()
    with open("assets/profile_results.txt", "w") as f:
        stats = pstats.Stats(profiler, stream=f)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.print_stats()

    # potential.initialiseAttributes()

    potential.debugger.printGroups()
    potential.debugger.printHeatMap()
    potential.debugger.printStringsText()
    potential.debugger.printGroupsText()