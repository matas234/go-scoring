import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

class Debugger:
    def __init__(self, score_instance) -> None:
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
                f.write(f"liberties: {group.liberties}\n")
                f.write(f"stability: {group.stability}\n")


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