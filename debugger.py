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
        

    def debug(self, path = "assets", history = 1) -> None:
        self.printHeatMap()
        self.printGroupsText(path, history)
        self.printStringsText(path, history)
        self.printBoard(path)


    def printGroupsText(self, path, history) -> None:
        rl = self.score.row_length
        with open(f"{path}/groups{history}.txt", "w", encoding="utf-8") as f:     
            f.write(f"🟢 for liberties \n")
            f.write(f"🔵 for territory \n")

            f.write(f"🔴 for double libs \n")
            f.write(f"🟣 for half libs \n")
            f.write(f"🟠 for third libs \n\n\n")
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

                for idx in group.third_liberties:
                    out_libs[idx // rl][idx % rl] = "🟠"

                for idx in group.half_liberties:
                    out_libs[idx // rl][idx % rl] = "🟣"

                for idx in group.double_liberties:
                    out_libs[idx // rl][idx % rl] = "🔴"

                for line_index in range(rl):
                    f.write(f"{"".join(out_libs[line_index])}   {"".join(out_ter[line_index])}  \n")

                f.write(f"eyes: {group.eyes}\n")  
                f.write(f"special eyes: {group.special_eyes}\n") 
                f.write(f"eye likes: {group.eye_likes}\n") 
                f.write(f"liberties: {group.liberties}\n")
                f.write(f"stability: {group.stability}\n")
                f.write(f"double liberties: {group.double_liberties}\n")
                f.write(f"half liberties: {group.half_liberties}\n")
                f.write(f"third liberties: {group.third_liberties}\n")
         #       f.write(f"territory: {group.territory}\n")


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

    def printStringsText(self, path = "assets", history = 1) -> None:
        rl = self.score.row_length
        with open(f"{path}/strings{history}.txt", "w", encoding="utf-8") as f:
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


    def printBoard(self, path = "assets") -> None:
        rl = self.score.row_length
        with open(f"{path}/board.txt", "a", encoding="utf-8") as f:
            out = [["🟤"]*rl for _ in range(rl)]
           
            for group in self.score.string_manager.groups:
                for idx in group.stones:
                    out[idx // rl][idx % rl] = "⚪" if group.nature == -1 else "⚫"

            for line in out:
                f.write(f"{''.join(line)}\n")
            f.write("\n\n\n\n")
            