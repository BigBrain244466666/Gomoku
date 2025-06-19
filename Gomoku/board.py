import pygame as pg
import time
BOARD_SIZE = 15
WIN_COUNT = 5

EMPTY = 0
PLAYER_BLACK = 1
PLAYER_WHITE = 2

class Board:
    def __init__(self, size):
        self.size = size
        self.grid = [[EMPTY for _ in range(self.size)] for _ in range(self.size)]
    
    def make_move(self, row, col, player):
        self.grid[row][col] = player

    def is_valid_move(self, r, c):
        status = False
        if r >= 0 and r <= (self.size - 1):
            if c >= 0 and c <= (self.size - 1):
                if self.grid[r][c] == EMPTY:
                    status = True
        return status

    def check_win(self, player):
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == player:
                    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
                    for dr, dc in directions:
                        count = 0
                        for i in range(WIN_COUNT):
                            nr, nc = r + i * dr, c + i * dc
                            if (0 <= nr <= self.size - 1 and 0 <= nc <= self.size - 1 and self.grid[nr][nc] == player):
                                count += 1
                            else:
                                break
                        if count == WIN_COUNT:
                            return True
        return False

    def is_board_full(self):
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == EMPTY:
                    return False
        return True
    
    def copy(self):
        new_board = Board(self.size)

        for r in range(self.size):
            for c in range(self.size):
                new_board.grid[r][c] = self.grid[r][c]

        return new_board