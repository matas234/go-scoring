import numpy as np

def loadGame(sgf_file):
    with open(sgf_file, 'r') as file:
        sgf_content = file.read().replace(')', "").replace('(', "").split('\n')

    board = np.zeros((19, 19), dtype=int)

    for move in sgf_content[14:-1]:
        if len(move) < 6: continue
        color = move[1]
        col = ord(move[3]) - ord('a')
        row = ord(move[4]) - ord('a')

        board[row][col] = -1 if color == 'W' else 1

    return board.flatten()