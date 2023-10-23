import numpy as np
import cv2
import os
import json
import copy

iterations = 0

def rotate(el, angle):
    elem = copy.deepcopy(el)
    elem['angle'] = angle

    if angle == 90:
        up = elem['colors']['up']
        elem['colors']['up'] = elem['colors']['right']
        elem['colors']['right'] = elem['colors']['down']
        elem['colors']['down'] = elem['colors']['left']
        elem['colors']['left'] = up

        up = elem['parts']['up']
        elem['parts']['up'] = elem['parts']['right']
        elem['parts']['right'] = elem['parts']['down']
        elem['parts']['down'] = elem['parts']['left']
        elem['parts']['left'] = up
        
    elif angle == -90:
        up = elem['colors']['up']
        elem['colors']['up'] = elem['colors']['left']
        elem['colors']['left'] = elem['colors']['down']
        elem['colors']['down'] = elem['colors']['right']
        elem['colors']['right'] = up

        up = elem['parts']['up']
        elem['parts']['up'] = elem['parts']['left']
        elem['parts']['left'] = elem['parts']['down']
        elem['parts']['down'] = elem['parts']['right']
        elem['parts']['right'] = up

    elif angle == 180:
        up = elem['colors']['up']
        elem['colors']['up'] = elem['colors']['down']
        elem['colors']['down'] = up
        left = elem['colors']['left']
        elem['colors']['left'] = elem['colors']['right']
        elem['colors']['right'] = left

        up = elem['parts']['up']
        elem['parts']['up'] = elem['parts']['down']
        elem['parts']['down'] = up
        left = elem['parts']['left']
        elem['parts']['left'] = elem['parts']['right']
        elem['parts']['right'] = left

    return elem

def is_valid(board, new_el_idx):
    global iterations
    iterations += 1

    i = new_el_idx[0]
    j = new_el_idx[1]
    current_el = copy.deepcopy(board[i][j])
    if current_el is not None:
        if i<2 and board[i+1][j] is not None: # check to down
            if current_el['colors']['down'] != board[i+1][j]['colors']['up']:
                return False
            elif current_el['parts']['down'] == board[i+1][j]['parts']['up']:
                return False
        if i>0 and board[i-1][j] is not None: # check to up
            if current_el['colors']['up'] != board[i-1][j]['colors']['down']:
                return False
            elif current_el['parts']['up'] == board[i-1][j]['parts']['down']:
                return False
        if j<2 and board[i][j+1] is not None: # check to right
            if current_el['colors']['right'] != board[i][j+1]['colors']['left']:
                return False
            elif current_el['parts']['right'] == board[i][j+1]['parts']['left']:
                return False
        if j>0 and board[i][j-1] is not None: # check to left
            if current_el['colors']['left'] != board[i][j-1]['colors']['right']:
                return False
            elif current_el['parts']['left'] == board[i][j-1]['parts']['right']:
                return False
        return True
    return False

def add_to_board(board_in, element):
    board = copy.deepcopy(board_in)
    new_el_idx = [None, None]
    added = False
    for i in range(3):
        for j in range(3):
            if board[i][j] == None:
                board[i][j] = copy.deepcopy(element)
                new_el_idx = [i, j]
                added = True
                break
        if added:
            break
    return board, new_el_idx

def solve_recursive(partial_solution, remaining_elements):
    if not remaining_elements:
        return partial_solution
    
    for element in remaining_elements:
        for rotation in [0, 90, -90, 180]:
            rotated_element = rotate(element, rotation)
            new_partial_solution, new_el_idx = add_to_board(partial_solution, rotated_element)

            if is_valid(new_partial_solution, new_el_idx):
                new_remaining_elements = copy.deepcopy(remaining_elements)
                new_remaining_elements.remove(element)
                result = solve_recursive(new_partial_solution, new_remaining_elements)
                if result:
                    return result
            
    return None


data_file = './data.json'
with open(data_file, 'r') as file:
    data = json.load(file)

for element in data['puzzle']:
    element['angle'] = 0

puzzle = copy.deepcopy(data['puzzle'])

board = [
    [None, None, None],
    [None, None, None],
    [None, None, None]
]

board = solve_recursive(board, puzzle)

print('Iterations: ', iterations)


# display solved image
dim = 300
solved_img = np.zeros((3*dim,3*dim,3), dtype=np.uint8)
for i in range(3):
    for j in range(3):
        image = cv2.imread('./imgs/'+board[i][j]['filename'])
        image = cv2.resize(image, (dim, dim))
        if board[i][j]['angle'] == 90:
            image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif board[i][j]['angle'] == -90:
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif board[i][j]['angle'] == 180:
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

        solved_img[i*dim:(i+1)*dim, j*dim:(j+1)*dim] = image

cv2.imshow('Solved puzzle', solved_img)
cv2.imwrite('./resources/solved.jpg', solved_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
