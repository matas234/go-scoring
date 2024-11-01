import numpy as np

def loadGame(sgf_file):
    """
    Load a 19x19 Go game from an SGF file
    Note if the game contains any captures, it will not work. 
    This is only for the purposes of loading example positions from demo games on ogs.

    Parameters
    ----------
    sgf_file : str
        The path to the SGF file

    Returns
    -------
    board : ndarray
        A 1D array of length 19*19, with 0 for empty, 1 for black and -1 for white
    """
    with open(sgf_file, 'r') as file:
        sgf_content = file.read().replace(')', "").replace('(', "").split('\n')

    board_size = int(sgf_content[11][3:5])
    board = np.zeros((board_size, board_size), dtype=int)
    offset = 1


    for move in sgf_content[14:-1]:
        if len(move) < 6: continue

        if move[1] == 'A': offset = 1
        color = move[1+offset]
        col = ord(move[3+offset]) - ord('a')
        row = ord(move[4+offset]) - ord('a')

        board[row][col] = -1 if color == 'W' else 1

    return board.flatten()