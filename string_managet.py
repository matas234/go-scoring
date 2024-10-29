from collections import defaultdict, deque
from typing import List

from scipy import ndimage

from group import Group
from string_go import String


class StringManager:
    def __init__(self, score_istance) -> None:
        self.score = score_istance
        self.strings: List[String] = []
        self.groups: List[Group] = []

        self.libs_to_groups: List[List[Group]] = [[] for _ in range(self.score.total_length)]


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
                    elif self.score.board[idx_new] == 0:
                        cur_string.addLiberty(idx_new)

        for idx in range(self.score.total_length):
            if self.score.board[idx] != 0 and not visited[idx]: 
                nature = self.score.board[idx]
                cur_string.nature = nature

                _dfs(idx)

                cur_string.generateConnectinos(self.score.row_length, self.score.board)
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

        # self.score.debugger.printTerritoryGroups(white_regions_sets, black_regions_sets)

        for group in self.groups:
            if group.nature == -1:
                group.territory = set.union(
                    *[(white_regions_sets[idx] - group.stones )
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





    def classifyLiberties(self) -> None:
        board = self.score.board
        cards = self.score._cardinals_cache
        double_libs = 9

        for group in self.groups:
            for lib in group.liberties:
                self.libs_to_groups[lib].append(group)


        for group in self.groups:
            for lib in group.liberties:
                lib_sharing_groups = self.libs_to_groups[lib]
                ### seki
                if len(lib_sharing_groups) == 2:
                    first = lib_sharing_groups[0]
                    second = lib_sharing_groups[1]

                    # if (first.nature != second.nature):
                    #     print("liberty shared by different coloured groups")
                    # if (2 <= len(first.liberties) <= 4):
                    #     print("first group has 2-4 liberties")
                    # if (2 <= len(second.liberties) <= 4):
                    #     print("second group has 2-4 liberties")
                    # if (len(first.stones) >= 3):
                    #     print("first group has at least 3 stones")
                    # if (len(second.stones) >= 3):
                    #     print("second group has at least 3 stones")
                    # if (first.liberties == second.liberties):
                    #     print("first and second group have the same liberties")

                    # print("")
                    if (first.nature != second.nature and
                        2 <= len(first.liberties) <= 4 and
                        2 <= len(second.liberties) <= 4 and
                        len(first.stones) >= 3 and
                        len(second.stones) >= 3 and
                        first.liberties == second.liberties
                    ):
                        
                        first.setAsStable()
                        second.setAsStable()


                    ### 
                 

                


        
    




        