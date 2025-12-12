import pygame as pg  # type: ignore
import Engine, AI, Rating

SCREEN_WIDTH = SCREEN_HEIGHT = 512
BOARD_TILES = 8
TILE_SIZE = SCREEN_HEIGHT // BOARD_TILES
FPS_LIMIT = 30
PIECE_IMAGES = {}
tile_colors = [pg.Color("white"), pg.Color("gray")]


def load_piece_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ',
              'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        PIECE_IMAGES[piece] = pg.transform.scale(
            pg.image.load("images/" + piece + ".png"), (TILE_SIZE, TILE_SIZE)
        )


def main():
    pg.init()
    window = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pg.time.Clock()
    window.fill(pg.Color("white"))

    game_state = Engine.ChessState()
    valid_moves = game_state.get_legal_moves()
    move_done = False
    animate_move = False

    load_piece_images()
    running = True
    selected_square = ()
    click_history = []
    match_over = False

    human_white = True
    human_black = False
    undo = False

    players = Rating.load_ratings() if hasattr(Rating, "load_ratings") else None
    if players:
        white_player = players.get("white", Rating.PlayerRating())
        black_player = players.get("black", Rating.PlayerRating())
    else:
        white_player = Rating.PlayerRating()
        black_player = Rating.PlayerRating()


    rating_updated = False

    while running:
        is_human_turn = (game_state.white_turn and human_white) or (not game_state.white_turn and human_black)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            elif event.type == pg.MOUSEBUTTONDOWN:
                if not match_over and is_human_turn:
                    mouse_pos = pg.mouse.get_pos()
                    col = mouse_pos[0] // TILE_SIZE
                    row = mouse_pos[1] // TILE_SIZE

                    if selected_square == (row, col):
                        selected_square = ()
                        click_history = []
                    else:
                        selected_square = (row, col)
                        click_history.append(selected_square)

                    if len(click_history) == 2:
                        move = Engine.Move(click_history[0], click_history[1], game_state.board)

                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                game_state.make_move(valid_moves[i])
                                move_done = True
                                animate_move = True
                                selected_square = ()
                                click_history = []
                                print(move.get_notation())
                        if not move_done:
                            click_history = [selected_square]

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_z:
                    game_state.undo_move()

                    if len(game_state.move_history) > 0 and (human_white & human_black) == False:
                        game_state.undo_move()
                    move_done = True
                    animate_move = False
                    selected_square = ()
                    click_history = []
                    match_over = False
                    undo = True

                    rating_updated = False
                elif event.key == pg.K_r:

                    game_state = Engine.ChessState()
                    valid_moves = game_state.get_legal_moves()
                    selected_square = ()
                    click_history = []
                    move_done = False
                    animate_move = False
                    match_over = False
                    undo = False
                    rating_updated = False

        if not match_over and not is_human_turn and not undo:
            ai_player = white_player if game_state.white_turn else black_player
            ai_move = AI.pick_best_move(game_state, valid_moves, ai_player.get_rating())
            if ai_move is None:
                ai_move = AI.pick_random_move(valid_moves)
            game_state.make_move(ai_move)
            move_done = True
            animate_move = True

        undo = False
        if move_done:
            if animate_move:
                animate_piece_movement(game_state.move_history[-1], window, game_state, clock)
            valid_moves = game_state.get_legal_moves()
            move_done = False
            animate_move = False

        render_game(window, game_state, valid_moves, selected_square, white_player, black_player)

        if game_state.checkmate:
            match_over = True

            if not rating_updated:
                if game_state.white_turn:
                    black_player.update(white_player.get_rating(), 1)
                    white_player.update(black_player.get_rating(), 0)
                    result_text = "Black wins by checkmate!"
                else:
                    white_player.update(black_player.get_rating(), 1)
                    black_player.update(white_player.get_rating(), 0)
                    result_text = "White wins by checkmate!"

                if hasattr(Rating, "save_ratings"):
                    Rating.save_ratings(white_player, black_player)

                window.fill(pg.Color("white"))
                draw_board(window)
                draw_pieces(window, game_state.board)
                draw_text(window, result_text, white_player.get_rating(), black_player.get_rating())
                pg.display.flip()


                pg.time.wait(4000)

                rating_updated = True

        elif game_state.stalemate:
            match_over = True

            if not rating_updated:
                white_player.update(black_player.get_rating(), 0.5)
                black_player.update(white_player.get_rating(), 0.5)

                if hasattr(Rating, "save_ratings"):
                    Rating.save_ratings(white_player, black_player)

                window.fill(pg.Color("white"))
                draw_board(window)
                draw_pieces(window, game_state.board)
                draw_text(window, "Stalemate", white_player.get_rating(), black_player.get_rating())
                pg.display.flip()

                pg.time.wait(4000)

                rating_updated = True


        clock.tick(FPS_LIMIT)
        pg.display.flip()


def highlight_tiles(window, game_state, valid_moves, selected_square):
    if selected_square != ():
        row, col = selected_square

        if game_state.board[row][col] != "--" and game_state.board[row][col][0] == ('w' if game_state.white_turn else 'b'):
            surface = pg.Surface((TILE_SIZE, TILE_SIZE))
            surface.set_alpha(100)
            surface.fill(pg.Color('blue'))
            window.blit(surface, (col * TILE_SIZE, row * TILE_SIZE))

            yellow = pg.Surface((TILE_SIZE, TILE_SIZE))
            yellow.set_alpha(100)
            yellow.fill(pg.Color('yellow'))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    window.blit(yellow, (move.end_col * TILE_SIZE, move.end_row * TILE_SIZE))


def render_game(window, game_state, valid_moves, selected_square, white_player, black_player):
    draw_board(window)
    highlight_tiles(window, game_state, valid_moves, selected_square)
    draw_pieces(window, game_state.board)


def draw_board(window):
    global tile_colors
    tile_colors = [pg.Color("darkGreen"), pg.Color("lightyellow")]
    for r in range(BOARD_TILES):
        for c in range(BOARD_TILES):
            color = tile_colors[(r + c) % 2]
            pg.draw.rect(window, color, pg.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))


def draw_pieces(window, board):
    for r in range(BOARD_TILES):
        for c in range(BOARD_TILES):
            piece = board[r][c]
            if piece != "--":
                window.blit(PIECE_IMAGES[piece], pg.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))


def animate_piece_movement(move, window, game_state, clock):
    global tile_colors
    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    frames_per_tile = 3
    total_frames = max(1, (abs(d_row) + abs(d_col)) * frames_per_tile)

    snapshot = [row.copy() for row in game_state.board]
    snapshot[move.start_row][move.start_col] = "--"
    snapshot[move.end_row][move.end_col] = move.piece_taken if move.piece_taken != "--" else "--"

    piece_image = PIECE_IMAGES[move.piece_moved]

    for frame in range(total_frames + 1):
        r = move.start_row + d_row * frame / total_frames
        c = move.start_col + d_col * frame / total_frames
        draw_board(window)
        draw_pieces(window, snapshot)

        end_square_color = tile_colors[(move.end_row + move.end_col) % 2]
        end_square = pg.Rect(move.end_col * TILE_SIZE, move.end_row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pg.draw.rect(window, end_square_color, end_square)
        if move.piece_taken != '--':
            window.blit(PIECE_IMAGES[move.piece_taken], end_square)

        window.blit(piece_image, pg.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        pg.display.flip()
        clock.tick(60)


def draw_text(window, text, white_rating=None, black_rating=None):
    font = pg.font.SysFont("Arial", 32, True, False)
    text_obj = font.render(text, True, pg.Color('black'))
    location = pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).move(
        SCREEN_WIDTH / 2 - text_obj.get_width() / 2,
        SCREEN_HEIGHT / 2 - text_obj.get_height() / 2
    )
    window.blit(text_obj, location)

    if white_rating is not None and black_rating is not None:
        rating_font = pg.font.SysFont("Arial", 24, False, False)
        rating_text = f"White: {white_rating} | Black: {black_rating}"
        rating_obj = rating_font.render(rating_text, True, pg.Color('black'))
        window.blit(rating_obj, (SCREEN_WIDTH / 2 - rating_obj.get_width() / 2, location.bottom + 20))


if __name__ == "__main__":
    main()
