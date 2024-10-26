import numpy as np

def loadGame(sgf_file):
    with open(sgf_file, 'r') as file:
        sgf_content = file.read().replace(')', "").replace('(', "").split('\n')

    board = np.zeros((19, 19), dtype=int)
    offset = 1

    for move in sgf_content[14:-1]:
        if len(move) < 6: continue

        if move[1] == 'A': offset = 1
        color = move[1+offset]
        col = ord(move[3+offset]) - ord('a')
        row = ord(move[4+offset]) - ord('a')

        board[row][col] = -1 if color == 'W' else 1

    return board.flatten()