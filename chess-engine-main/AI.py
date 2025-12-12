import random
from Rating import load_ratings, save_ratings, PlayerRating

CHECKMATE = 10000
STALEMATE = 0
DEFAULT_DEPTH = 2 
piece_scores = {
    "K": 0, 
    "Q": 9,
    "R": 5,
    "B": 3,
    "N": 3,
    "p": 1
}

ratings = load_ratings()
white_player = ratings["white"]
black_player = ratings["black"]



def get_ai_parameters(rating):
    if rating < 1000:
        return {"depth": 1, "randomness": 0.4}
    elif rating < 1300:
        return {"depth": 2, "randomness": 0.3}
    elif rating < 1600:
        return {"depth": 3, "randomness": 0.2}
    elif rating < 1900:
        return {"depth": 4, "randomness": 0.1}
    else:
        return {"depth": 5, "randomness": 0.05}


def pick_best_move(game_state, valid_moves, ai_rating):
    params = get_ai_parameters(ai_rating)
    depth = params["depth"]
    randomness = params["randomness"]

    global next_move
    next_move = None
    random.shuffle(valid_moves)

    # Add randomness for weaker AIs
    if random.random() < randomness:
        return random.choice(valid_moves)

    # Start search and remember starting depth
    alpha_beta(game_state, valid_moves, depth, -CHECKMATE, CHECKMATE, game_state.white_turn, ai_rating, starting_depth=depth)

    # Fallback if no move was chosen
    if next_move is None and valid_moves:
        print(" AI failed to find a move, picking random fallback.")
        return random.choice(valid_moves)

    return next_move


def alpha_beta(game_state, valid_moves, depth, alpha, beta, white_turn, ai_rating, starting_depth):
    global next_move

    # Stop at leaf or stalemate/checkmate
    if depth == 0 or len(valid_moves) == 0:
        return evaluate_board(game_state.board, ai_rating)

    if white_turn:
        max_eval = -CHECKMATE
        for move in order_moves(valid_moves):
            game_state.make_move(move)
            next_moves = game_state.get_legal_moves()
            eval_score = alpha_beta(game_state, next_moves, depth - 1, alpha, beta, False, ai_rating, starting_depth)
            game_state.undo_move()

            if eval_score > max_eval:
                max_eval = eval_score
                # Only set next_move at the *root* call
                if depth == starting_depth:
                    next_move = move

            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval

    else:
        min_eval = CHECKMATE
        for move in order_moves(valid_moves):
            game_state.make_move(move)
            next_moves = game_state.get_legal_moves()
            eval_score = alpha_beta(game_state, next_moves, depth - 1, alpha, beta, True, ai_rating, starting_depth)
            game_state.undo_move()

            if eval_score < min_eval:
                min_eval = eval_score
                if depth == starting_depth:
                    next_move = move

            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval



def order_moves(moves):
    return sorted(moves, key=lambda m: m.piece_taken != "--", reverse=True)


def evaluate_board(board, ai_rating=1200):
    score = 0
    for row in board:
        for square in row:
            if square != "--":
                piece_type = square[1]
                piece_value = piece_scores[piece_type]
                if square[0] == 'w':
                    score += piece_value
                else:
                    score -= piece_value

    skill_factor = min(max(ai_rating, 800), 2000)
    noise = random.uniform(-1, 1) * (2000 - skill_factor) / 800
    return score + noise


def pick_random_move(valid_moves):

    if valid_moves:
        return random.choice(valid_moves)
    return None


def update_and_save_ratings(result):

    white_player.update(black_player.rating, result)
    black_player.update(white_player.rating, 1 - result)
    save_ratings(white_player, black_player)
    print(f"New Ratings — White: {white_player.get_rating()}, Black: {black_player.get_rating()}")
