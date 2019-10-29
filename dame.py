
import numpy as np
import pygame, sys
from pygame.locals import *

WINDOWWIDTH = 1280  # size of window's width in pixels
WINDOWHEIGHT = 720  # size of windows' height in pixels
BOXSIZE = 90        # size of box height & width in pixels
NRB = 8             # number of boxes
MARGIN = 0          # size of gap between boxes in pixels
LINE_WIDTH = 3      # For odd width values, the thickness of each line grows with the original line being in the cent
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

#                 #  R    G    B
BACKGROUND_COLOR = (153, 255, 153)
LINE_COLOR       = (  0,   0, 255)
HIGHLIGHTCOLOR   = ( 60,  60, 100)
player1_image = pygame.image.load("emoji1.png")
player2_image = pygame.image.load("emoji2.png")
clean_box = pygame.image.load("clean_box.png")

directions = [(-1, -1), (-1, 0), (-1, +1), (0, -1), (0, +1), (+1, -1), (+1, 0), (+1, -1)]


def display_board():
    pygame.init()
    pygame.display.set_caption('DAME-VARIANTA')
    DISPLAYSURF.fill(BACKGROUND_COLOR)
    for line in range(0, NRB * BOXSIZE + 1, BOXSIZE):
        pygame.draw.line(DISPLAYSURF, LINE_COLOR, (MARGIN + line, MARGIN), (MARGIN + line, MARGIN + NRB * BOXSIZE), LINE_WIDTH)
        pygame.draw.line(DISPLAYSURF, LINE_COLOR, (MARGIN, MARGIN + line), (MARGIN + NRB * BOXSIZE, MARGIN + line), LINE_WIDTH)


def clear_box(x, y):
    DISPLAYSURF.blit(clean_box, (x, y))


class ProblemState:
    # -1 sus && +1 jos
    def __init__(self):
        self.square = np.zeros((8, 8))
        self.square[0] = np.ones(8).dot(-1)
        self.square[7] = np.ones(8)
        self.moves_next = 1

    def __str__(self):
        res = ""
        for i in self.square:
            res += str([str(int(j)) if j >= 0 else '-' for j in i]) + '\n'
        res += "Next: " + str(self.moves_next)
        return res


# -1 jos || +1 sus || cineva e blocat
def is_final_state(state):
    if np.max(state.square[0]) == np.min(state.square[7]) == 1:
        return "1 win"
    if np.max(state.square[0]) == np.min(state.square[7]) == -1:
        return "-1 win"
    # blocat
    return False


def is_valid_transition(state, x, y, new_x, new_y):
    #   validam pozitiile si existenta pieselor curente
    if new_x and new_y not in range(0, 8):
        return False
    if state.square[new_x][new_y]:
        return False
    if x and y not in range(0, 8):
        return False
    if not state.square[x][y]:
        return False

    #  validam saritura efectiv
    for direction in directions:
        if x + direction[0] == new_x and y + direction[1] == new_y:
            return True

    return False


def make_transition(state, x, y, new_x, new_y):
    state.square[x][y] = 0
    state.square[new_x][new_y] = state.moves_next
    state.moves_next *= (-1)


def play(s):
    display_board()
    #  (Handles events. Updates the game state.  Draws the game state to the screen.)
    coord_from = False
    coord_to = False
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()


        pygame.display.update()


if __name__ == '__main__':
    s = ProblemState()
    print(s)
    play(s)


