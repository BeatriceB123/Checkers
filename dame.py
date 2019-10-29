
import numpy as np
import pygame, sys
from pygame.locals import *

WINDOWWIDTH =  720  # size of window's width in pixels
WINDOWHEIGHT = 720  # size of windows' height in pixels
BOXSIZE = 90        # size of box height & width in pixels
NRB = 8             # number of boxes
LINE_WIDTH = 4      # For odd width values, the thickness of each line grows with the original line being in the cent
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

#                 #  R    G    B
BACKGROUND_COLOR = (153, 255, 153)
LINE_COLOR       = (  0,   0, 255)
HIGHLIGHTCOLOR   = ( 60,  60, 100)
player1_image = pygame.image.load("emoji1.png")
player2_image = pygame.image.load("emoji2.png")
clean_box = pygame.image.load("clean_box.png")
selected_player1_image = pygame.image.load("selected_emoji1.png")
selected_player2_image = pygame.image.load("selected_emoji2.png")

directions = [(-1, -1), (-1, 0), (-1, +1), (0, -1), (0, +1), (+1, -1), (+1, 0), (+1, +1)]
dict_image_coordinates = dict([((i, j), (j * BOXSIZE, i * BOXSIZE)) for i in range(0, 8) for j in range(0, 8)])
coord_from = None


class ProblemState:
    # -1 sus && +1 jos
    # -1 va fi calculatorul
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


def display_board():
    pygame.init()
    pygame.display.set_caption('DAME-VARIANTA')
    DISPLAYSURF.fill(BACKGROUND_COLOR)
    for line in range(0, NRB * BOXSIZE + 1, BOXSIZE):
        pygame.draw.line(DISPLAYSURF, LINE_COLOR, (line, 0), (line, NRB * BOXSIZE), LINE_WIDTH)
        pygame.draw.line(DISPLAYSURF, LINE_COLOR, (0, line), (NRB * BOXSIZE, line), LINE_WIDTH)


def update_board(state):
    for i in range(0, 8):
        for j in range(0, 8):
            coordx, coordy = dict_image_coordinates[(i, j)]
            if state.square[i][j] == 0:
                DISPLAYSURF.blit(clean_box, (coordx, coordy))
            elif state.square[i][j] == 1:
                DISPLAYSURF.blit(player1_image, (coordx, coordy))
            elif state.square[i][j] == -1:
                DISPLAYSURF.blit(player2_image, (coordx, coordy))
            elif state.square[i][j] == 2:
                DISPLAYSURF.blit(selected_player1_image, (coordx, coordy))
            elif state.square[i][j] == -2:
                DISPLAYSURF.blit(selected_player2_image, (coordx, coordy))


def select_or_unselect_box(state, select, coordx, coordy):
    if select == 1:
        state.square[coordx][coordy] = 2 * np.sign(state.square[coordx][coordy])
    elif select == -1:
        state.square[coordx][coordy] = 1 * np.sign(state.square[coordx][coordy])


def determine_coordinates_box(e):
    cari = NRB
    carj = NRB
    if e[0] and e[1] in range(0, NRB * BOXSIZE + 1):  # in square
        for k in range(NRB, 0, -1):
            if e[0] < k * BOXSIZE:
                carj = k - 1
            if e[1] < k * BOXSIZE:
                cari = k - 1
        return cari, carj
    return None


def process_the_event(state, e):
    global coord_from
    position = determine_coordinates_box(e)  # coord i si j in matrice
    if not position:
        print("Se vrea implementarea chestiilor de pe margine, a butoanelor")

    if not coord_from:   # ne pregatim sa facem o mutare cu piesa de pe from
        coord_from = position
        select_or_unselect_box(state, 1, *coord_from)
    elif coord_from:
        select_or_unselect_box(state, -1, *coord_from)  # deselectam piesa pe care vrem sa o mutam
        if is_valid_transition(state, coord_from[0], coord_from[1], *position):   # verificam mutarea
            make_transition(state, coord_from[0], coord_from[1], *position)       # facem mutarea
            select_or_unselect_box(state, -1, *coord_from)                        # redesenam
        if is_final_state(state):
            print("End of game" + is_final_state(state))
        coord_from = None
    return None


# -1 jos || +1 sus || cineva e blocat
def is_final_state(state):
    if np.max(state.square[0]) == np.min(state.square[0]) == 1:
        return "1 win"
    if np.max(state.square[7]) == np.min(state.square[7]) == -1:
        return "-1 win"
    # de implementat cazul in care e blocat
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


def computer_move(state):
    while state.moves_next == -1:
        computer_coord_from = np.random.choice(range(0, 8), 2, p=np.ones(8).dot(0.125))
        computer_coord_to = np.random.choice(range(0, 8), 2, p=np.ones(8).dot(0.125))
        if is_valid_transition(state, computer_coord_from[0], computer_coord_from[1], *computer_coord_to):
            if state.square[computer_coord_from[0]][computer_coord_from[1]] == -1:
                make_transition(state, computer_coord_from[0], computer_coord_from[1], *computer_coord_to)


def play(state):
    display_board()
    update_board(state)
    while True:
        update_board(state)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                process_the_event(state, event.pos)
                print(coord_from, '\n', state)
        update_board(state)
        pygame.display.update()

        if state.moves_next == -1:  # CPU turn
            computer_move(state)
            update_board(state)
            pygame.display.update()
            print(state)


if __name__ == '__main__':
    problem_state = ProblemState()
    play(problem_state)

