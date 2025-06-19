from board import *

def evaluate_board(board_object, current_player):
    grid = board_object.grid
    size = board_object.size


    two_in_a_row = 10
    three_in_a_row = 100
    blocked_three = 50      
    open_four = 1000         
    blocked_four = 500       
    five_in_a_row = float('inf')

    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    total_points = 0
    for r in range(size):
        for c in range(size):
            if grid[r][c] == EMPTY:
                continue

            current_player_stone = grid[r][c]
            opponent_player_stone = PLAYER_BLACK if current_player_stone == PLAYER_WHITE else PLAYER_WHITE
            opponent_player = PLAYER_BLACK if current_player == PLAYER_WHITE else PLAYER_WHITE


            for dr, dc in directions:
                prev_r, prev_c = r - dr, c - dc
                if 0 <= prev_r < size and 0 <= prev_c < size and grid[prev_r][prev_c] == current_player_stone:
                    continue
                back_blocked = False

                if not (0 <= prev_r < size and 0 <= prev_c < size):
                    back_blocked = True
                elif grid[prev_r][prev_c] == opponent_player_stone:
                    back_blocked = True 

                current_chain_length = 0


                for i in range(WIN_COUNT):
                    nr, nc = r + i * dr, c + i * dc
                    if not (0 <= nr < size and 0 <= nc < size):
                        break
                    if grid[nr][nc] == current_player_stone:
                        current_chain_length += 1
                    else:
                        break               
                if current_chain_length == 0:
                    continue 

                end_r, end_c = r + current_chain_length * dr, c + current_chain_length * dc

                front_blocked = False
                if not (0 <= end_r < size and 0 <= end_c < size):
                    front_blocked = True
                elif grid[end_r][end_c] == opponent_player_stone:
                    front_blocked = True

                score_value = 0

                if current_player_stone == current_player:
                    if current_chain_length >= WIN_COUNT:
                        if current_player_stone == current_player:
                            score_value = five_in_a_row

                    elif current_chain_length == 4:
                        if not (back_blocked or front_blocked):
                            score_value = open_four
                        elif back_blocked != front_blocked:
                            score_value = blocked_four

                    elif current_chain_length == 3:
                        if not (back_blocked or front_blocked):
                            score_value = three_in_a_row
                        elif back_blocked != front_blocked:
                            score_value = blocked_three

                    elif current_chain_length == 2:
                        if not (back_blocked or front_blocked):
                            score_value = two_in_a_row

                elif current_player_stone == opponent_player:
                        if current_chain_length >= WIN_COUNT:
                            score_value = -five_in_a_row
                            return score_value

                        elif current_chain_length == 4:
                            if not (back_blocked or front_blocked):
                                score_value = -(open_four * 3)
                            elif back_blocked != front_blocked:
                                score_value = -(blocked_four * 3)

                        elif current_chain_length == 3:
                            if not (back_blocked or front_blocked):
                                score_value = -(three_in_a_row * 3)
                            elif back_blocked != front_blocked:
                                score_value = -(blocked_three * 3)

                        elif current_chain_length == 2:
                            if not (back_blocked or front_blocked):
                                score_value = -(two_in_a_row * 3)
                
                total_points += score_value

    
    return total_points

def get_best_move(board_object, current_player):
    best_score = -float('inf')
    best_move = None
    current_player_stone = current_player
    for r in range(board_object.size):
        for c in range(board_object.size):
            current_move_score = 0
            if board_object.is_valid_move(r, c): 
                temp_board = board_object.copy()
                temp_board.make_move(r, c, current_player_stone)
                current_move_score += evaluate_board(temp_board, current_player_stone)
                if current_move_score > best_score:
                    best_score = current_move_score
                    best_move = (r, c)
    return best_move

def minimax_alpha_beta(board_object, depth, current_player, maximizing_player, alpha, beta):
    if depth == 0:
        return evaluate_board(board_object, current_player), (15,15)

    if maximizing_player:
        max_eval = -float('inf')
        best_move = None
        for r in range(board_object.size):
            for c in range(board_object.size):
                if board_object.is_valid_move(r, c):
                    temp_board = board_object.copy()
                    temp_board.make_move(r, c, current_player)
                    eval, _ = minimax_alpha_beta(temp_board, depth - 1, current_player, False, alpha, beta)
                    if eval > max_eval:
                        max_eval = eval
                        best_move = (r, c)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        opponent_player = PLAYER_BLACK if current_player == PLAYER_WHITE else PLAYER_WHITE
        for r in range(board_object.size):
            for c in range(board_object.size):
                if board_object.is_valid_move(r, c):
                    temp_board = board_object.copy()
                    temp_board.make_move(r, c, opponent_player)
                    eval, _ = minimax_alpha_beta(temp_board, depth - 1, current_player, True, alpha, beta)
                    if eval < min_eval:
                        min_eval = eval
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            if beta <= alpha:
                break

        return min_eval, best_move

def get_best_move_minimax_alpha_beta(board_object, current_player, depth):
    score, move = minimax_alpha_beta(board_object, depth, current_player, True, -float('inf'), float('inf'))
    if move == None:
        move = get_best_move(board_object, current_player)

    return move