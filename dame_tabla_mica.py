import random
import numpy as np
import pygame, sys
from pygame.locals import *

BOXSIZE = 90        # size of box height & width in pixels
NRB = 4             # number of boxes
WINDOWWIDTH = NRB * BOXSIZE  # size of window's width in pixels
WINDOWHEIGHT = NRB * BOXSIZE  # size of windows' height in pixels
LINE_WIDTH = 4      # For odd width values, the thickness of each line grows with the original line being in the cent
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
oo = 9999

#                 #  R    G    B
BACKGROUND_COLOR = (153, 255, 153)
LINE_COLOR       = (  0,   0, 255)
HIGHLIGHT_COLOR  = ( 60,  60, 100)

player1_image = pygame.image.load("emoji1.png")
player2_image = pygame.image.load("emoji2.png")
clean_box = pygame.image.load("clean_box.png")
valid_box = pygame.image.load("valid_box.png")
selected_player1_image = pygame.image.load("selected_emoji1.png")
selected_player2_image = pygame.image.load("selected_emoji2.png")


directions = [(-1, -1), (-1, 0), (-1, +1), (0, -1), (0, +1), (+1, -1), (+1, 0), (+1, +1)]

# each position from the matrix has a correspondent in the drawn square, measured in pixels
list_for_indices = [(i, j) for i in range(NRB) for j in range(NRB)]
dict_image_coordinates = dict([((i, j), (j * BOXSIZE, i * BOXSIZE)) for i, j in list_for_indices])


# if we have a selected piece
coord_from = None

my_file = open("results.txt", "w")


class ProblemState:
    # -1 sus && +1 jos, iar -1 va fi calculatorul.
    def __init__(self):
        self.square = np.zeros((NRB, NRB))
        self.square[0] = np.ones(NRB).dot(-1)
        self.square[NRB-1] = np.ones(NRB)
        self.moves_next = 1

    def __str__(self):
        res = ""
        for i in self.square:
            res += str([str(int(j)) if j >= 0 else '-' for j in i]) + '\n'
        res += "Next: " + str(self.moves_next)
        return res


def copy_state(state):
    other = ProblemState()
    other.square = np.array(state.square, copy=True)
    other.moves_next = state.moves_next
    return other


def clean_board():
    DISPLAYSURF.fill(HIGHLIGHT_COLOR)
    for line in range(0, NRB * BOXSIZE + 1, BOXSIZE):
        pygame.draw.line(DISPLAYSURF, LINE_COLOR, (line, 0), (line, NRB * BOXSIZE), LINE_WIDTH)
        pygame.draw.line(DISPLAYSURF, LINE_COLOR, (0, line), (NRB * BOXSIZE, line), LINE_WIDTH)


def update_board(state):
    clean_board()
    for i, j in list_for_indices:
        coordx, coordy = dict_image_coordinates[(i, j)]
        coordx += LINE_WIDTH/2+1
        coordy += LINE_WIDTH/2+1
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
        elif state.square[i][j] == 3:
            DISPLAYSURF.blit(valid_box, (coordx, coordy))


def print_final_message(win):
    pygame.time.wait(1_000)
    DISPLAYSURF.fill(BACKGROUND_COLOR)
    font = pygame.font.SysFont("comicsansms", 72)
    str_message = "Equality"
    if win == 1:
        str_message = "You won"
    elif win == -1:
        str_message = "I won"
    text = font.render(str_message, True, (0, 128, 0))
    DISPLAYSURF.blit(text, (350 - text.get_width() // 2, 250 - text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(1_000)


# daca selectam o piesa, o marcam atat pe ea, cat si tranzitiile valide
# daca o deselectam, vom demarca tot ce am marcat pentru ea
def select_or_unselect_box(state, select, coordx, coordy):
    if select == 1:
        state.square[coordx][coordy] = 2 * np.sign(state.square[coordx][coordy])
    elif select == -1:
        state.square[coordx][coordy] = 1 * np.sign(state.square[coordx][coordy])

    for direction in directions:
        newx = coordx + direction[0]
        newy = coordy + direction[1]
        if is_valid_transition(state, coordx, coordy, newx, newy):
            state.square[newx][newy] = 3 if select == 1 else 0
    return state


# primeste evenimentul - pe ce s-a apasat, si returneaza din ce careu face parte piesa
def determine_coordinates_box(e):
    cari = NRB
    carj = NRB
    if e[0] and e[1] in range(NRB * BOXSIZE + 1):  # in square
        for k in range(NRB, 0, -1):
            if e[0] < k * BOXSIZE:
                carj = k - 1
            if e[1] < k * BOXSIZE:
                cari = k - 1
        return cari, carj
    return None


# daca coord_from era selectat, inseamna ca suntem in mijlocul unei mutari ce trebuie validata
# daca nu, il setam acum
def process_the_event(state, e):
    global coord_from
    position = determine_coordinates_box(e)  # coord i si j in matrice
    if not position:
        print("Se vrea implementarea chestiilor de pe margine, a butoanelor")

    if state.square[position[0]][position[1]] == 1:  # e alegerea unei noi piese personale
        if coord_from:  # se va deselecta piesa veche; "o vom suprascrie"
            state = select_or_unselect_box(state, -1, *coord_from)
        coord_from = position
        state = select_or_unselect_box(state, 1, *coord_from)
    elif coord_from:       # se incearca o mutare
        state = select_or_unselect_box(state, -1, *coord_from)  # deselectam piesa pe care vrem sa o mutam
        if is_valid_transition(state, coord_from[0], coord_from[1], *position):   # verificam mutarea
            state = make_transition(state, coord_from[0], coord_from[1], *position)       # facem mutarea
            state = select_or_unselect_box(state, -1, *coord_from)                        # redesenam
        coord_from = None
    return state


# -1 jos || +1 sus
def is_final_state(state):
    if np.max(state.square[0]) == np.min(state.square[0]) == 1:
        return 1
    if np.max(state.square[NRB-1]) == np.min(state.square[NRB-1]) == -1:
        return -1
    return False


def is_valid_transition(state, x, y, new_x, new_y):
    #   validam pozitiile si existenta pieselor curente
    if (new_x not in range(NRB)) or (new_y not in range(NRB)):
        return False
    if state.square[new_x][new_y] != 0 and state.square[new_x][new_y] != 3:
        return False
    if (x not in range(NRB)) or (y not in range(NRB)):
        return False
    if state.square[x][y] == 0:
        return False

    #  validam saritura efectiv
    for direction in directions:
        if x + direction[0] == new_x and y + direction[1] == new_y:
            return True

    return False


def make_transition(state, x, y, new_x, new_y):
    new_state = copy_state(state)
    new_state.square[x][y] = 0
    new_state.square[new_x][new_y] = state.moves_next
    new_state.moves_next *= (-1)
    return new_state


def get_player_score(state):
    score_player = 0
    for i, j in list_for_indices:
        if state.square[i][j] in [1, 2] and i != 0:
            score_player += NRB - 1 - i
        elif state.square[i][j] in [1, 2] and i == 0:  # pozitia finala va avea mai multe puncte
            score_player += NRB + 10
    return score_player


def get_ai_score(state):
    score_ai = 0
    for i, j in list_for_indices:
        if state.square[i][j] in [-1, -2] and i != NRB - 1:  # CPU
            score_ai += i
        elif state.square[i][j] in [-1, -2] and i == NRB - 1:  # pozitia finala va avea mai multe puncte
            score_ai += NRB + 10
    return score_ai


def get_state_score_naive(state):
    return get_ai_score(state) - get_player_score(state)


def get_possible_actions_from(state):
    res = []
    for i, j in list_for_indices:
        if state.square[i][j] == state.moves_next:
            for direction in directions:
                new_i = i + direction[0]
                new_j = j + direction[1]
                if is_valid_transition(state, i, j, new_i, new_j):
                    res.append((i, j, new_i, new_j))
    return res


def computer_moves_based_on_one_level_results(state):
    li = []   # list of possible states, with maximum scores
    max_score = -oo
    possible_moves = get_possible_actions_from(state)
    for i, j, new_i, new_j in possible_moves:
        new_state = make_transition(state, i, j, new_i, new_j)
        new_score = get_state_score_naive(new_state)
        if new_score == max_score:
            li.append((new_state, new_score, i, j, new_i, new_j))
        elif new_score > max_score:
            li = [(new_state, new_score, i, j, new_i, new_j)]
            max_score = new_score
    chosed_move = random.choice(li)
    state = make_transition(state, chosed_move[2], chosed_move[3], chosed_move[4], chosed_move[5])
    return state


# returneaza actiunea cea mai buna, si valoarea care se obtine cu ea
'''
def minmax(state, is_maximized_level, current_depth, maxim_depth):
    if current_depth > maxim_depth or is_final_state(state):
        return (None, None, None, None), get_state_score_naive(state)

    all_val = []
    for i, j, new_i, new_j in get_possible_actions_from(state):
        aux = make_transition(state, i, j, new_i, new_j)
        val = minmax(aux, 1 - is_maximized_level, current_depth + 1, maxim_depth)
        all_val.append([(i, j, new_i, new_j), val[1]])

    if is_maximized_level == 1:
        best_result = -oo
        best_results = []
        for aux, v in all_val:
            if state.square[aux[0]][aux[1]] == -1:
                if v > best_result:
                    best_results = [(aux, v)]
                    best_result = v
                elif v == best_result:
                    best_results.append([aux, v])
    else:
        best_result = oo
        best_results = []
        for aux, v in all_val:
            if state.square[aux[0]][aux[1]] == +1:
                if v < best_result:
                    best_results = [(aux, v)]
                    best_result = v
                elif v == best_result:
                    best_results.append([aux, v])
    if current_depth == 0:
        print("Valorile din toate pozitiile: ", all_val)
        print("Ce am ales: ", best_results)
        print("Iar valoare tablei acum este: ", best_results[0][1])
    return best_results[0][0]
'''


def minmax(state, is_maximized_level, current_depth, maxim_depth):
    if current_depth > maxim_depth or is_final_state(state):
        return get_state_score_naive(state)
    if is_maximized_level == 1:
        best_result = -oo
        possible_moves = get_possible_actions_from(state)
        for i, j, new_i, new_j in possible_moves:
            best_result = max(best_result, minmax(make_transition(state, i, j, new_i, new_j), 0, current_depth + 1, maxim_depth))
        return best_result
    else:
        best_result = oo
        possible_moves = get_possible_actions_from(state)
        for i, j, new_i, new_j in possible_moves:
            best_result = min(best_result, minmax(make_transition(state, i, j, new_i, new_j), 1, current_depth + 1, maxim_depth))
        return best_result


def play(state):
    pygame.init()
    pygame.display.set_caption('DAME-VARIANT')
    update_board(state)
    while True:
        if is_final_state(state):
            print_final_message(is_final_state(state))
            break
        if state.moves_next == 1:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONUP:
                    state = process_the_event(state, event.pos)
                    print("Scor dupa mutarea jucatorului: ", get_state_score_naive(state))
            update_board(state)
            pygame.display.update()

        elif state.moves_next == -1:  # CPU turn
            # state = computer_moves_random(state)
            # state = computer_moves_based_on_one_level_results(state)
            aux = minmax(state, 1, 0, 2)
            state = make_transition(state, *aux)
            print("Scor dupa mutarea CPU: ", get_state_score_naive(state))
            update_board(state)
            pygame.display.update()


if __name__ == '__main__':
    play(ProblemState())

