import os
import numpy as np


def load_dataset_game(dir_path = r"C:\Users\msaba\Documents\GitHub\scored-games"):
    files = os.listdir(dir_path)

    for file in files:
        with open(os.path.join(dir_path, file), 'r') as f:
            sgf_content = f.read().split('\n')

        for i, move in enumerate(sgf_content):
            if "- -" in move:
                content = sgf_content[i+1:i+20]
                break

        for idx, line in enumerate(content):
            content[idx] = line[3:-2]

        board = np.zeros(361, dtype=int)

        for i in range(19):
            for j in range(19):
                if content[i][j*2] == "x":
                    board[i*19 + j] = 1
                elif content[i][j*2] == "o":
                    board[i*19 + j] = -1

        yield board
