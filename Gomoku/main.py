# Credits:
# Board image: https://www.istockphoto.com/nl/search/2/image-film?phrase=empty+wooden+board+top+view
# White stone: https://www.jansjewels.com/35mm-Opaque-White-Round-FB-Stone_p_37150.html
# Black stone: https://www.indiamart.com/proddetail/black-round-onyx-gemstone-16070146448.html
# Background music: Echoes in Blue by Tokyo Music Walker | https://soundcloud.com/user-356546060
#                   Music promoted by https://www.chosic.com/free-music/all/
#                   Creative Commons CC BY 3.0
#                   https://creativecommons.org/licenses/by/3.0/
 

import pygame as pg
from pygame import mixer
import sys
import time
from board import *
from ai_player import *
import os

BOARD_SIZE = 15
SCREEN_WIDTH, SCREEN_HEIGHT = 550, 550
GRID_SPACING = SCREEN_WIDTH // BOARD_SIZE
BOARD_PADDING = GRID_SPACING // 2
BOARD_COLOUR = (240, 200, 140)
LINE_COLOUR = (0, 0, 0)
BLACK_STONE_COLOUR = (0, 0, 0)
WHITE_STONE_COLOUR = (255, 255, 255)
STONE_RADIUS = (GRID_SPACING // 2) - 5
HIGHLIGHT_COLOR = (255, 0, 0)

print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
starting = True
starting_player = input("Who wants to go first?\nYou: 1 | Bot: 2\n")
while starting:
    if starting_player == "1" or starting_player == "2":
        starting_player = int(starting_player)
        starting = False
    else:
        starting_player = input("Please enter 1 for YOU to start, 2 for BOT to start: ")

starting = True
difficulty = input("What difficulty do you want?\nEasy: 1 | Hard: 2 (Moves will take longer to make)\n")
while starting:
    if difficulty == "1" or difficulty == "2":
        difficulty = int(difficulty)
        starting = False
    else:
        difficulty = input("Please enter 1 for EASY, 2 for HARD (Moves will take longer to make): ")

starting = True
cheats = input("Do you want cheats on?\nYES: 1 | NO: 2\n")
while starting:
    if cheats == "1" or cheats == "2":
        cheats = int(cheats)
        starting = False
    else:
        cheats = input("Please enter 1 for YES, 2 for NO: ")
        
print("Good luck! (Click on the screen to play)")

class Game:
    def __init__(self):
        pg.init()
        self.board_size = BOARD_SIZE
        self.grid_spacing = GRID_SPACING
        self.padding = BOARD_PADDING
        
        self.screen_width = (self.board_size - 1) * self.grid_spacing
        self.screen_height = (self.board_size - 1) * self.grid_spacing
        self.real_screen_width = self.screen_width + self.padding * 2
        self.real_screen_height = self.screen_height + self.padding * 2
        self.background = pg.image.load('board.jpg')
        self.background = pg.transform.scale(self.background, (self.real_screen_width, self.real_screen_height + 50))
        self.white_stone = pg.image.load('white_stone.png')
        self.white_stone = pg.transform.scale(self.white_stone, (STONE_RADIUS * 2 + 5, STONE_RADIUS * 2 + 5))
        self.black_stone = pg.image.load('black_stone.png')
        self.black_stone = pg.transform.scale(self.black_stone, (STONE_RADIUS * 2 + 5, STONE_RADIUS * 2 + 5))
        self.screen = pg.display.set_mode((self.real_screen_width, self.real_screen_height + 50))
        pg.display.set_caption("Gomoku")
        self.running = True
        self.board = Board(self.board_size)

        self.current_player = starting_player
        self.game_over = False
        self.winner = None

    def draw_board(self):
        self.screen.blit(self.background, (0, 0))        
        for i in range(self.board_size):
            pg.draw.line(self.screen, LINE_COLOUR, 
                         (self.padding + i * self.grid_spacing, self.padding), 
                         (self.padding + i * self.grid_spacing, self.screen_height + self.padding), 
                         2)
            pg.draw.line(self.screen, LINE_COLOUR, 
                         (self.padding, self.padding + i * self.grid_spacing), 
                         (self.screen_width + self.padding, self.padding + i * self.grid_spacing), 
                         2)

    def draw_stones(self):
        for r in range(self.board_size):
            for c in range(self.board_size):
                cell_value = self.board.grid[r][c]
                
                self.center_x = self.padding + c * self.grid_spacing
                self.center_y = self.padding + r * self.grid_spacing

                if cell_value == PLAYER_BLACK:
                    self.screen.blit(self.black_stone, (self.center_x - STONE_RADIUS - 2.5, self.center_y - STONE_RADIUS - 2.5))
                elif cell_value == PLAYER_WHITE:
                    self.screen.blit(self.white_stone, (self.center_x - STONE_RADIUS - 2.5, self.center_y - STONE_RADIUS - 2.5))

    def get_board_coords(self, mouse_pos):
        x, y = mouse_pos
        x -= self.padding
        y -= self.padding
        col = round(x / self.grid_spacing)
        row = round(y / self.grid_spacing)
        
        col = max(0, min(col, self.board_size))
        row = max(0, min(row, self.board_size))
        
        return row, col
    
    def draw_text(self, text, font_size, colour, x, y):
        font = pg.font.Font(None, font_size)
        text_surface = font.render(text, True, colour)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def button(self, text, x, y, width, height, colour, font_size, screen, font_colour):
        pg.draw.rect(screen, colour, [x, y, width, height])
        font = pg.font.Font(None, font_size)
        text_surface = font.render(text, True, font_colour)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)

    def run(self, difficulty):
        mixer.init()
        mixer.music.load("background.mp3")
        mixer.music.set_volume(1)
        mixer.music.play(-1)
        
        place_sound = pg.mixer.Sound("piece_sound.mp3")
        place_sound.set_volume(10)
        prev_ai_row, prev_ai_col = 7, 7
        self.winning = None

        welcome = True
        while welcome:
            self.screen.blit(self.background, (0, 0))  
            lines = [
            "WELCOME TO GOMOKU!",
            "",
            "Objective: Be the first player to get exactly",
            "five of your stones in an unbroken line.",
            "",
            "Players: Two players: one uses black stones",
            "2one uses white stones.",
            "",
            "Board: Played on the intersections of a",
            "grid (e.g., 15x15 lines).",
            "",
            "Turns: Players alternate placing one of their ",
            "stones on any empty intersection, with",
            "the player starting first",
            "",
            "Winning Line: The line can be horizontal,",
            "vertical, or diagonal.",
            "",
            "Stones: Once placed, stones cannot be",
            "moved or removed.",
            "",
            "Draw: If the board fills completely and no",
            "player has achieved five in a row.",
            "",
            "Click ENTER to begin"
            ]
            font = pg.font.Font('freesansbold.ttf', 20)

            y_offset = (self.real_screen_height + 50) // 2 - (len(lines) * font.get_linesize()) // 2

            for line in lines:
                text = font.render(line, True, "black")
                text_rect = text.get_rect(center=(self.real_screen_width // 2, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += font.get_linesize()
            pg.display.update()

            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        welcome = False
        while self.running:
            if evaluate_board(self.board, PLAYER_BLACK) > 0:
                self.winning = "BLACK"
            elif evaluate_board(self.board, PLAYER_BLACK) < 0:
                self.winning = "WHITE"
            else:
                self.winning = "DRAW"

            mixer.music.set_volume(0.5)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if not self.game_over:
                    if event.type == pg.MOUSEBUTTONDOWN:
                        mouse_pos = event.pos
                        if (self.real_screen_width // 4 - 40) <= mouse_pos[0] <= (self.real_screen_width // 4 + 40) and (self.real_screen_height) <= mouse_pos[1] <= (self.real_screen_height + 35):
                            self.board = Board(BOARD_SIZE)
                            self.current_player = starting_player
                            prev_ai_row, prev_ai_col = 7, 7
                        if (self.real_screen_width // 4 * 3 - 40) <= mouse_pos[0] <= (self.real_screen_width // 4 * 3 + 40) and (self.real_screen_height) <= mouse_pos[1] <= (self.real_screen_height + 35):
                            self.running = False

                    if self.current_player == PLAYER_BLACK:
                        if event.type == pg.MOUSEBUTTONDOWN:
                            mouse_pos = event.pos
                            row, col = self.get_board_coords(mouse_pos)
                            if self.board.is_valid_move(row, col):
                                self.board.make_move(row, col, self.current_player)
                                place_sound.play()
                                print(f"You moved to ({row}, {col})")
                                
                                if self.board.check_win(self.current_player) == True:
                                    self.game_over = True
                                    if self.current_player == PLAYER_BLACK:
                                        self.winner = "Black (Human)"
                                    if self.current_player == PLAYER_WHITE:
                                        self.winner = "White (AI)"
                                elif self.board.is_board_full == True:
                                    self.winner = "Draw"
                                
                                else:
                                    self.current_player = PLAYER_WHITE
                            else:
                                print(f"Invalid move at ({row}, {col}). Try again.")
                    elif self.current_player == PLAYER_WHITE:
                        loop = True
                        ai = False
                        while loop:
                            for r in range(self.board_size):
                                for c in range(self.board_size):
                                    if self.board.grid[r][c] == self.current_player:
                                        loop = False
                                        ai = True
                                    elif self.board.grid == Board(BOARD_SIZE).grid:
                                        ai = False
                                        loop = False
                                        ai_row, ai_col = 7, 7
                                if loop == False:
                                    break
                            if loop == False:
                                break         
                            ai_row, ai_col = row, col + 1
                            if not self.board.is_valid_move(ai_row, ai_col):
                                loop = False
                                ai = True
                            loop = False
                        if ai:
                            ai_row, ai_col = get_best_move_minimax_alpha_beta(self.board, self.current_player, int(difficulty))
                            prev_ai_row, prev_ai_col = ai_row, ai_col
                        if ai_row is not None and ai_col is not None:
                            time.sleep(0.5)
                            self.board.make_move(ai_row, ai_col, PLAYER_WHITE)
                            self.draw_board()
                            self.draw_stones()
                            place_sound.play()
                            print(f"AI moved to ({ai_row}, {ai_col})")
                            self.draw_board()
                            self.draw_stones()
                            if self.board.check_win(self.current_player):
                                self.current_player = PLAYER_BLACK
                                self.game_over = True
                                self.winner = "White (AI)"
                            elif self.board.is_board_full():
                                self.current_player = PLAYER_BLACK
                                self.game_over = True
                                self.winner = "Draw"
                            else:
                                self.current_player = PLAYER_BLACK
                        else:
                            print("AI could not find a valid move. This shouldn't happen in a non-full board.")
                            self.game_over = True

            self.draw_board()
            self.draw_stones()
            self.button("Restart", self.real_screen_width // 4 - 40, self.real_screen_height, 80, 35, "brown", 30, self.screen, "white")
            if cheats == 1:
                self.button(f"Winning: {self.winning}", self.real_screen_width // 2 - 80, self.real_screen_height, 160, 35, "brown", 27, self.screen, "white")
            self.button("Quit", self.real_screen_width // 4 * 3 - 40, self.real_screen_height, 80, 35, "brown", 30, self.screen, "white")
            if self.current_player == PLAYER_BLACK:
                pg.draw.circle(self.screen, "black", (self.padding + prev_ai_col * self.grid_spacing, self.padding + prev_ai_row * self.grid_spacing), 5)
            

            if self.game_over == True:
                mixer.music.set_volume(1.5)
                if self.winner == "Draw":
                    self.draw_text("It's a Draw!", 60, HIGHLIGHT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                else:
                    self.draw_text(f"{self.winner} Wins!", 60, HIGHLIGHT_COLOR, self.real_screen_width // 2, self.real_screen_height // 2)
                pg.display.flip()
                time.sleep(4)
                while self.game_over:
                    self.screen.blit(self.background, (0, 0))
                    if self.winner == "Draw":
                        self.draw_text("It's a Draw!", 60, HIGHLIGHT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                    else:
                        self.draw_text(f"{self.winner} Wins!", 60, HIGHLIGHT_COLOR, self.real_screen_width // 2, self.real_screen_height // 2)
                    self.button("Restart", self.real_screen_width // 4 - 40, self.real_screen_height, 80, 35, "brown", 30, self.screen, "white")
                    self.button("Quit", self.real_screen_width // 4 * 3 - 40, self.real_screen_height, 80, 35, "brown", 30, self.screen, "white")
                    for event in pg.event.get():
                        if event.type == pg.QUIT:
                            self.game_over = False
                            self.running = False
                            break
                        if event.type == pg.MOUSEBUTTONDOWN:
                            mouse_pos = event.pos
                            if (self.real_screen_width // 4 - 40) <= mouse_pos[0] <= (self.real_screen_width // 4 + 40) and (self.real_screen_height) <= mouse_pos[1] <= (self.real_screen_height + 35):
                                self.board = Board(BOARD_SIZE)
                                prev_ai_row, prev_ai_col = 7, 7
                                self.game_over = False
                                self.current_player = starting_player
                                break
                            if (self.real_screen_width // 4 * 3 - 40) <= mouse_pos[0] <= (self.real_screen_width // 4 * 3 + 40) and (self.real_screen_height) <= mouse_pos[1] <= (self.real_screen_height + 35):
                                self.game_over = False
                                self.running = False
                                break
                    pg.display.flip()

            pg.display.flip()
        pg.quit()
        sys.exit()

my_game = Game()
my_game.run(difficulty)