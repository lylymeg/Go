import pygame
import sys

pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 850, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jeu de Go (Mini 9x9)")
clock = pygame.time.Clock()

# Grille 9x9
BOARD_SIZE = 9
CELL_SIZE = 60
GRID_OFFSET_X = 80
GRID_OFFSET_Y = 80

# Couleurs (Thème Bois Traditionnel & Pierres Néon)
BG_COLOR = (20, 24, 33)
BOARD_BG = (215, 175, 120)  # Couleur bois clair
GRID_LINE = (90, 65, 40)
BLACK_STONE = (30, 30, 30)
WHITE_STONE = (240, 240, 240)
HIGHLIGHT_COLOR = (0, 255, 157)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)

# Polices
font_medium = pygame.font.SysFont("Arial", 22, bold=True)
font_small = pygame.font.SysFont("Arial", 16)

def reset_game():
    return {
        "board": [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
        "turn": 1,  # 1 pour Noir, 2 pour Blanc
        "captures": {1: 0, 2: 0},
        "pass_count": 0,
        "game_over": False,
        "message": "Tour du joueur : NOIR"
    }

game = reset_game()

def get_group(board, r, c):
    """Trouve toutes les pierres connectées du même groupe et leurs libertés"""
    color = board[r][c]
    if color == 0:
        return set(), set()
    
    group = set()
    liberties = set()
    to_visit = [(r, c)]
    
    while to_visit:
        curr_r, curr_c = to_visit.pop()
        if (curr_r, curr_c) in group:
            continue
        group.add((curr_r, curr_c))
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = curr_r + dr, curr_c + dc
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                if board[nr][nc] == 0:
                    liberties.add((nr, nc))
                elif board[nr][nc] == color and (nr, nc) not in group:
                    to_visit.append((nr, nc))
                    
    return group, liberties

def play_move(board, r, c, player):
    """Joue un coup et applique les règles de capture et suicide"""
    opponent = 2 if player == 1 else 1
    
    # Copie temporaire pour tester le coup
    new_board = [row[:] for row in board]
    new_board[r][c] = player
    
    captured_stones = set()
    
    # 1. Vérifier les captures sur les groupes adjacents ennemis
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
            if new_board[nr][nc] == opponent:
                opp_group, opp_liberties = get_group(new_board, nr, nc)
                if len(opp_liberties) == 0:
                    captured_stones.update(opp_group)
                    
    # Retirer les pierres capturées
    for cr, cc in captured_stones:
        new_board[cr][cc] = 0
        
    # 2. Vérifier le suicide (si le groupe posé n'a aucune liberté et n'a rien capturé)
    self_group, self_liberties = get_group(new_board, r, c)
    if len(self_liberties) == 0 and len(captured_stones) == 0:
        return False, board, 0  # Coup illégal (suicide)
        
    # Appliquer définitivement sur le plateau
    for cr, cc in captured_stones:
        board[cr][cc] = 0
    board[r][c] = player
    
    return True, board, len(captured_stones)

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game["game_over"]:
                game = reset_game()
            else:
                # Vérifier si le clic est sur le bouton Passer
                pass_btn = pygame.Rect(WIDTH - 220, 180, 185, 45)
                if pass_btn.collidepoint(mouse_pos):
                    game["pass_count"] += 1
                    if game["pass_count"] >= 2:
                        game["game_over"] = True
                        game["message"] = "Partie terminée (2 passes consécutives)"
                    else:
                        game["turn"] = 2 if game["turn"] == 1 else 1
                        player_name = "NOIR" if game["turn"] == 1 else "BLANC"
                        game["message"] = f"Joueur a passé. Tour de : {player_name}"
                    continue

                # Convertir la position de la souris en coordonnées de grille
                board_pixel_size = (BOARD_SIZE - 1) * CELL_SIZE
                # Trouver l'intersection la plus proche
                c = round((mouse_pos[0] - GRID_OFFSET_X) / CELL_SIZE)
                r = round((mouse_pos[1] - GRID_OFFSET_Y) / CELL_SIZE)
                
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    if game["board"][r][c] == 0:
                        success, new_board, caps = play_move(game["board"], r, c, game["turn"])
                        if success:
                            game["board"] = new_board
                            game["captures"][game["turn"]] += caps
                            game["pass_count"] = 0
                            game["turn"] = 2 if game["turn"] == 1 else 1
                            player_name = "NOIR" if game["turn"] == 1 else "BLANC"
                            game["message"] = f"Tour du joueur : {player_name}"
                        else:
                            game["message"] = "Coup illégal (Suicide interdit) !"

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game["game_over"]:
                game = reset_game()

    screen.fill(BG_COLOR)

    # 1. Dessin du plateau de Go (Bois)
    board_rect = pygame.Rect(
        GRID_OFFSET_X - 25, 
        GRID_OFFSET_Y - 25, 
        (BOARD_SIZE - 1) * CELL_SIZE + 50, 
        (BOARD_SIZE - 1) * CELL_SIZE + 50
    )
    pygame.draw.rect(screen, BOARD_BG, board_rect, border_radius=10)
    pygame.draw.rect(screen, GRID_LINE, board_rect, 3, border_radius=10)

    # Lignes de la grille
    for i in range(BOARD_SIZE):
        start_x = GRID_OFFSET_X
        start_y = GRID_OFFSET_Y + i * CELL_SIZE
        end_x = GRID_OFFSET_X + (BOARD_SIZE - 1) * CELL_SIZE
        end_y = start_y
        pygame.draw.line(screen, GRID_LINE, (start_x, start_y), (end_x, end_y), 2)

        start_x = GRID_OFFSET_X + i * CELL_SIZE
        start_y = GRID_OFFSET_Y
        end_x = start_x
        end_y = GRID_OFFSET_Y + (BOARD_SIZE - 1) * CELL_SIZE
        pygame.draw.line(screen, GRID_LINE, (start_x, start_y), (end_x, end_y), 2)

    # Étoiles de repère sur le goban 9x9 (Hoshi)
    hoshi_points = [(2, 2), (2, 6), (6, 2), (6, 6), (4, 4)]
    for hr, hc in hoshi_points:
        hx = GRID_OFFSET_X + hc * CELL_SIZE
        hy = GRID_OFFSET_Y + hr * CELL_SIZE
        pygame.draw.circle(screen, GRID_LINE, (hx, hy), 4)

    # 2. Dessin des pierres
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            val = game["board"][r][c]
            if val != 0:
                px = GRID_OFFSET_X + c * CELL_SIZE
                py = GRID_OFFSET_Y + r * CELL_SIZE
                color = BLACK_STONE if val == 1 else WHITE_STONE
                # Ombre de la pierre
                pygame.draw.circle(screen, (10, 10, 10), (px + 2, py + 2), CELL_SIZE // 2 - 4)
                # Pierre principale
                pygame.draw.circle(screen, color, (px, py), CELL_SIZE // 2 - 4)
                # Reflet lumineux sur la pierre noire
                if val == 1:
                    pygame.draw.circle(screen, (70, 70, 70), (px - 4, py - 4), 4)

    # 3. Panneau latérale (Scores, Tour, Boutons)
    panel_x = GRID_OFFSET_X + (BOARD_SIZE - 1) * CELL_SIZE + 45
    
    title_txt = font_medium.render("JEU DE GO (9x9)", True, WHITE)
    screen.blit(title_txt, (panel_x, 80))

    turn_color = BLACK_STONE if game["turn"] == 1 else WHITE_STONE
    pygame.draw.circle(screen, turn_color, (panel_x + 15, 135), 10)
    turn_txt = font_small.render(game["message"], True, WHITE)
    screen.blit(turn_txt, (panel_x + 35, 125))

    # Bouton Passer
    pass_btn = pygame.Rect(panel_x, 180, 185, 45)
    pygame.draw.rect(screen, (50, 60, 80), pass_btn, border_radius=8)
    pass_txt = font_small.render("Passer son tour", True, WHITE)
    screen.blit(pass_txt, (pass_btn.centerx - pass_txt.get_width() // 2, pass_btn.centery - pass_txt.get_height() // 2))

    # Captures
    cap_black = font_small.render(f"Captures Noires : {game['captures'][1]}", True, GRAY)
    cap_white = font_small.render(f"Captures Blanches : {game['captures'][2]}", True, GRAY)
    screen.blit(cap_black, (panel_x, 250))
    screen.blit(cap_white, (panel_x, 280))

    # Instructions
    inst1 = font_small.render("Commandes :", True, WHITE)
    inst2 = font_small.render("- Clic sur intersection : Poser une pierre", True, GRAY)
    inst3 = font_small.render("- 2 passes consécutives : Fin de partie", True, GRAY)
    screen.blit(inst1, (panel_x, 350))
    screen.blit(inst2, (panel_x, 380))
    screen.blit(inst3, (panel_x, 410))

    if game["game_over"]:
        over_txt = font_medium.render("PARTIE TERMINÉE (ESPACE)", True, HIGHLIGHT_COLOR)
        screen.blit(over_txt, (panel_x, 480))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()