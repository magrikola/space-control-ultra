import pygame
import sys
import math

pygame.init()

GRID_SIZE = 4
CELL_SIZE = 100
TOP_MARGIN = 80
BOTTOM_MARGIN = 80
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE + TOP_MARGIN + BOTTOM_MARGIN
MAX_DEPTH = 4

BACKGROUND = (245, 248, 255)
TEXT_COLOR = (20, 20, 20)
BLOCKED_CELL = (140, 140, 140)
EMPTY_CELL = (204, 229, 255)
PLAYER_COLOR = (255, 105, 180)
AI_COLOR = (170, 110, 255)
HIGHLIGHT = (255, 255, 255)
BUTTON_COLOR = (230, 230, 235)
BUTTON_HOVER = (210, 210, 220)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Control Ultra")

font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 28)
clock = pygame.time.Clock()


class SpaceControlUltra:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.player_pos = (0, 0)
        self.ai_pos = (GRID_SIZE - 1, GRID_SIZE - 1)
        self.current_turn = "player"
        self.game_over = False
        self.winner = None
        self.status_text = "Your turn"
        self.restart_rect = None

    def get_valid_moves(self, pos, board, player_pos, ai_pos):
        row, col = pos
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        moves = []

        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc

            if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
                if board[new_row][new_col] == 0 and (new_row, new_col) != player_pos and (new_row, new_col) != ai_pos:
                    moves.append((new_row, new_col))

        return moves

    def evaluate_state(self, board, player_pos, ai_pos):
        ai_move_count = len(self.get_valid_moves(ai_pos, board, player_pos, ai_pos))
        player_move_count = len(self.get_valid_moves(player_pos, board, player_pos, ai_pos))
        return ai_move_count - player_move_count

    def minimax(self, board, player_pos, ai_pos, depth, is_maximizing):
        ai_moves = self.get_valid_moves(ai_pos, board, player_pos, ai_pos)
        player_moves = self.get_valid_moves(player_pos, board, player_pos, ai_pos)

        if not ai_moves:
            return -100
        if not player_moves:
            return 100

        if depth == 0:
            return self.evaluate_state(board, player_pos, ai_pos)

        if is_maximizing:
            best_value = -math.inf

            for move in ai_moves:
                copied_board = [row[:] for row in board]
                old_row, old_col = ai_pos
                copied_board[old_row][old_col] = 1
                new_ai_pos = move

                score = self.minimax(copied_board, player_pos, new_ai_pos, depth - 1, False)
                best_value = max(best_value, score)

            return best_value

        else:
            best_value = math.inf

            for move in player_moves:
                copied_board = [row[:] for row in board]
                old_row, old_col = player_pos
                copied_board[old_row][old_col] = 1
                new_player_pos = move

                score = self.minimax(copied_board, new_player_pos, ai_pos, depth - 1, True)
                best_value = min(best_value, score)

            return best_value

    def get_best_ai_move(self):
        valid_moves = self.get_valid_moves(self.ai_pos, self.board, self.player_pos, self.ai_pos)
        best_score = -math.inf
        best_move = None

        for move in valid_moves:
            copied_board = [row[:] for row in self.board]
            old_row, old_col = self.ai_pos
            copied_board[old_row][old_col] = 1

            score = self.minimax(copied_board, self.player_pos, move, MAX_DEPTH - 1, False)

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def move_player(self, new_pos):
        old_row, old_col = self.player_pos
        self.board[old_row][old_col] = 1
        self.player_pos = new_pos

    def move_ai(self, new_pos):
        old_row, old_col = self.ai_pos
        self.board[old_row][old_col] = 1
        self.ai_pos = new_pos

    def check_game_over(self):
        player_moves = self.get_valid_moves(self.player_pos, self.board, self.player_pos, self.ai_pos)
        ai_moves = self.get_valid_moves(self.ai_pos, self.board, self.player_pos, self.ai_pos)

        if self.current_turn == "player" and not player_moves:
            self.game_over = True
            self.winner = "AI"
            self.status_text = "AI won!"
            return True

        if self.current_turn == "ai" and not ai_moves:
            self.game_over = True
            self.winner = "Player"
            self.status_text = "You won!"
            return True

        return False

    def handle_player_click(self, mouse_pos):
        if self.game_over or self.current_turn != "player":
            return

        mouse_x, mouse_y = mouse_pos

        if mouse_y < TOP_MARGIN or mouse_y >= TOP_MARGIN + GRID_SIZE * CELL_SIZE:
            return

        col = mouse_x // CELL_SIZE
        row = (mouse_y - TOP_MARGIN) // CELL_SIZE

        if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
            return

        clicked_cell = (row, col)
        valid_moves = self.get_valid_moves(self.player_pos, self.board, self.player_pos, self.ai_pos)

        if clicked_cell in valid_moves:
            self.move_player(clicked_cell)
            self.current_turn = "ai"
            self.status_text = "AI is thinking..."

            if self.check_game_over():
                return

    def handle_ai_turn(self):
        if self.game_over or self.current_turn != "ai":
            return

        pygame.time.delay(250)
        best_move = self.get_best_ai_move()

        if best_move is not None:
            self.move_ai(best_move)

        self.current_turn = "player"

        if self.check_game_over():
            return

        self.status_text = "Your turn"

    def draw_restart_button(self, screen):
        button_width = 180
        button_height = 45
        button_x = (WIDTH - button_width) // 2
        button_y = HEIGHT - 60

        self.restart_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        mouse_pos = pygame.mouse.get_pos()
        if self.restart_rect.collidepoint(mouse_pos):
            current_button_color = BUTTON_HOVER
        else:
            current_button_color = BUTTON_COLOR

        pygame.draw.rect(screen, current_button_color, self.restart_rect, border_radius=10)
        pygame.draw.rect(screen, TEXT_COLOR, self.restart_rect, 2, border_radius=10)

        button_text = small_font.render("Restart", True, TEXT_COLOR)
        text_rect = button_text.get_rect(center=self.restart_rect.center)
        screen.blit(button_text, text_rect)

    def draw(self, screen):
        screen.fill(BACKGROUND)

        status_surface = font.render(self.status_text, True, TEXT_COLOR)
        screen.blit(status_surface, (20, 20))

        valid_player_moves = self.get_valid_moves(self.player_pos, self.board, self.player_pos, self.ai_pos)

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = col * CELL_SIZE
                y = row * CELL_SIZE + TOP_MARGIN
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

                color = EMPTY_CELL

                if self.board[row][col] == 1:
                    color = BLOCKED_CELL

                if (row, col) == self.player_pos:
                    color = PLAYER_COLOR
                elif (row, col) == self.ai_pos:
                    color = AI_COLOR

                pygame.draw.rect(screen, color, rect)

                if not self.game_over and self.current_turn == "player":
                    if (row, col) in valid_player_moves:
                        pygame.draw.rect(screen, HIGHLIGHT, rect, 4)

                pygame.draw.rect(screen, TEXT_COLOR, rect, 2)

        player_row, player_col = self.player_pos
        ai_row, ai_col = self.ai_pos

        player_text = font.render("You", True, TEXT_COLOR)
        ai_text = font.render("AI", True, TEXT_COLOR)

        screen.blit(player_text, (player_col * CELL_SIZE + 38, player_row * CELL_SIZE + TOP_MARGIN + 30))
        screen.blit(ai_text, (ai_col * CELL_SIZE + 38, ai_row * CELL_SIZE + TOP_MARGIN + 30))

        if self.game_over:
            self.draw_restart_button(screen)


def main():
    game = SpaceControlUltra()
    running = True

    while running:
        clock.tick(60)

        if game.current_turn == "ai" and not game.game_over:
            game.handle_ai_turn()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if game.game_over:
                        if game.restart_rect is not None and game.restart_rect.collidepoint(event.pos):
                            game.reset_game()
                    else:
                        game.handle_player_click(event.pos)

        game.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()