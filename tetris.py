import pygame
import random
import os
from pygame import Rect

# Initialize Pygame
pygame.init()

# Game dimensions
CELL_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT
SIDEBAR_WIDTH = 200

# Colors - Enhanced with more vibrant colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)
GRID_COLOR = (40, 40, 40)
CYAN = (0, 240, 240)      # I piece
YELLOW = (240, 240, 0)    # O piece
PURPLE = (160, 0, 240)    # T piece
GREEN = (0, 240, 0)       # S piece
RED = (240, 0, 0)         # Z piece
BLUE = (0, 0, 240)        # J piece
ORANGE = (240, 160, 0)    # L piece

# Tetromino shapes and colors - Enhanced with more detailed shapes
SHAPES = [
    [[1, 1, 1, 1]],                  # I
    [[1, 1], [1, 1]],                # O
    [[0, 1, 0], [1, 1, 1]],          # T
    [[0, 1, 1], [1, 1, 0]],          # S
    [[1, 1, 0], [0, 1, 1]],          # Z
    [[1, 0, 0], [1, 1, 1]],          # J
    [[0, 0, 1], [1, 1, 1]],           # L
    [[1, 1], [1, 1], [0, 1], [1, 1]] # Semicolon
]

# Main colors for each piece
COLORS = [CYAN, YELLOW, PURPLE, GREEN, RED, BLUE, ORANGE, GRAY]

# Darker shade for 3D effect
DARK_COLORS = [
    (0, 180, 180),    # Dark Cyan
    (180, 180, 0),    # Dark Yellow
    (120, 0, 180),    # Dark Purple
    (0, 180, 0),      # Dark Green
    (180, 0, 0),      # Dark Red
    (0, 0, 180),      # Dark Blue
    (180, 120, 0),    # Dark Orange
    DARK_GRAY         # Dark Gray
]

# Lighter shade for 3D effect
LIGHT_COLORS = [
    (120, 255, 255),  # Light Cyan
    (255, 255, 120),  # Light Yellow
    (200, 120, 255),  # Light Purple
    (120, 255, 120),  # Light Green
    (255, 120, 120),  # Light Red
    (120, 120, 255),  # Light Blue
    (255, 200, 120),  # Light Orange
    WHITE             # White
]

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH + SIDEBAR_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 24)
title_font = pygame.font.SysFont('Arial', 36, bold=True)

# Background grid pattern
background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
background.fill(BLACK)
for y in range(GRID_HEIGHT):
    for x in range(GRID_WIDTH):
        pygame.draw.rect(background, GRID_COLOR, 
                        (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

class Tetromino:
    def __init__(self, x, y, shape_index):
        self.x = x
        self.y = y
        self.shape_index = shape_index
        self.shape = SHAPES[shape_index]
        self.color = COLORS[shape_index]
        self.dark_color = DARK_COLORS[shape_index]
        self.light_color = LIGHT_COLORS[shape_index]
        self.rotation = 0

    def rotate(self):
        # Create a new rotated shape
        rows = len(self.shape)
        cols = len(self.shape[0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        
        for r in range(rows):
            for c in range(cols):
                rotated[c][rows - 1 - r] = self.shape[r][c]
        
        return rotated

    def get_position_blocks(self, shape=None):
        if shape is None:
            shape = self.shape
            
        blocks = []
        for i in range(len(shape)):
            for j in range(len(shape[i])):
                if shape[i][j]:
                    blocks.append((self.x + j, self.y + i))
        return blocks
        
    def draw(self, surface, offset_x=0, offset_y=0):
        blocks = self.get_position_blocks()
        for x, y in blocks:
            if y >= 0:  # Only draw if the block is within the visible grid
                # Calculate the position on the screen
                rect_x = offset_x + x * CELL_SIZE
                rect_y = offset_y + y * CELL_SIZE
                
                # Draw the block with 3D effect
                # Main block
                pygame.draw.rect(surface, self.color, 
                                (rect_x + 1, rect_y + 1, CELL_SIZE - 2, CELL_SIZE - 2))
                
                # Highlight (top and left edges)
                pygame.draw.line(surface, self.light_color, 
                                (rect_x + 2, rect_y + 2), 
                                (rect_x + CELL_SIZE - 3, rect_y + 2), 2)
                pygame.draw.line(surface, self.light_color, 
                                (rect_x + 2, rect_y + 2), 
                                (rect_x + 2, rect_y + CELL_SIZE - 3), 2)
                
                # Shadow (bottom and right edges)
                pygame.draw.line(surface, self.dark_color, 
                                (rect_x + 2, rect_y + CELL_SIZE - 3), 
                                (rect_x + CELL_SIZE - 3, rect_y + CELL_SIZE - 3), 2)
                pygame.draw.line(surface, self.dark_color, 
                                (rect_x + CELL_SIZE - 3, rect_y + 2), 
                                (rect_x + CELL_SIZE - 3, rect_y + CELL_SIZE - 3), 2)

class TetrisGame:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.grid_colors = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5  # seconds per grid cell
        self.fall_time = 0
        self.paused = False
        self.ghost_piece = None
        self.update_ghost_piece()
        
        # Start screen flag
        self.game_started = False
        
        # Animation variables
        self.lines_to_clear = []
        self.clear_animation_time = 0
        self.clear_animation_duration = 0.5  # seconds
        self.is_animating = False

    def new_piece(self):
        shape_index = random.randint(0, len(SHAPES) - 1)
        # Start position: centered horizontally, at the top of the grid
        x = GRID_WIDTH // 2 - len(SHAPES[shape_index][0]) // 2
        y = 0
        return Tetromino(x, y, shape_index)

    def valid_position(self, piece, shape=None):
        blocks = piece.get_position_blocks(shape)
        for x, y in blocks:
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                return False
            if y >= 0 and self.grid[y][x]:
                return False
        return True

    def update_ghost_piece(self):
        if self.current_piece:
            self.ghost_piece = Tetromino(
                self.current_piece.x,
                self.current_piece.y,
                self.current_piece.shape_index
            )
            self.ghost_piece.shape = self.current_piece.shape
            
            # Move ghost piece down until it hits something
            while self.valid_position(self.ghost_piece):
                self.ghost_piece.y += 1
            
            # Move back up one step
            self.ghost_piece.y -= 1

    def lock_piece(self):
        blocks = self.current_piece.get_position_blocks()
        for x, y in blocks:
            if y >= 0:  # Only lock if the block is within the grid
                self.grid[y][x] = 1
                self.grid_colors[y][x] = {
                    'main': self.current_piece.color,
                    'dark': self.current_piece.dark_color,
                    'light': self.current_piece.light_color
                }
            
        self.check_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        self.update_ghost_piece()
        
        # Check for game over
        if not self.valid_position(self.current_piece):
            self.game_over = True

    def check_lines(self):
        self.lines_to_clear = []
        for i in range(GRID_HEIGHT):
            if all(self.grid[i]):
                self.lines_to_clear.append(i)
        
        if self.lines_to_clear:
            self.is_animating = True
            self.clear_animation_time = 0

    def clear_lines(self):
        for line in self.lines_to_clear:
            del self.grid[line]
            del self.grid_colors[line]
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            self.grid_colors.insert(0, [None for _ in range(GRID_WIDTH)])
        
        # Update score and level
        if self.lines_to_clear:
            self.lines_cleared += len(self.lines_to_clear)
            self.score += (100 * len(self.lines_to_clear)) * len(self.lines_to_clear)  # More points for multiple lines
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)  # Speed up as level increases
            
        self.lines_to_clear = []
        self.is_animating = False

    def move(self, dx, dy):
        self.current_piece.x += dx
        self.current_piece.y += dy
        
        if not self.valid_position(self.current_piece):
            self.current_piece.x -= dx
            self.current_piece.y -= dy
            
            # If we tried to move down and couldn't, lock the piece
            if dy > 0:
                self.lock_piece()
                return False
            return False
            
        self.update_ghost_piece()
        return True

    def rotate_piece(self):
        rotated_shape = self.current_piece.rotate()
        if self.valid_position(self.current_piece, rotated_shape):
            self.current_piece.shape = rotated_shape
            self.update_ghost_piece()
            return True
        return False

    def drop(self):
        while self.move(0, 1):
            pass
        # Lock piece is called in move() when it can't move down anymore

    def update(self, dt):
        if not self.game_started or self.paused or self.game_over:
            return
            
        if self.is_animating:
            self.clear_animation_time += dt
            if self.clear_animation_time >= self.clear_animation_duration:
                self.clear_lines()
            return
            
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            self.move(0, 1)

    def draw(self, screen):
        # Draw the background grid
        screen.blit(background, (0, 0))
        
        # If game hasn't started yet, show start screen
        if not self.game_started:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            # Draw title
            title_text = title_font.render("TETRIS", True, WHITE)
            text_width = title_text.get_width()
            screen.blit(title_text, (SCREEN_WIDTH // 2 - text_width // 2, SCREEN_HEIGHT // 2 - 80))
            
            # Draw start instruction
            start_text = font.render("Press S to Start", True, YELLOW)
            text_width = start_text.get_width()
            screen.blit(start_text, (SCREEN_WIDTH // 2 - text_width // 2, SCREEN_HEIGHT // 2))
            
            # Draw controls
            controls_text = font.render("Controls:", True, WHITE)
            text_width = controls_text.get_width()
            screen.blit(controls_text, (SCREEN_WIDTH // 2 - text_width // 2, SCREEN_HEIGHT // 2 + 50))
            
            controls = [
                "← → : Move",
                "↑ : Rotate",
                "↓ : Soft Drop",
                "Space : Hard Drop",
                "P : Pause"
            ]
            
            for i, control in enumerate(controls):
                ctrl_text = font.render(control, True, WHITE)
                text_width = ctrl_text.get_width()
                screen.blit(ctrl_text, (SCREEN_WIDTH // 2 - text_width // 2, SCREEN_HEIGHT // 2 + 80 + i * 25))
                
            return
        
        # Draw the ghost piece
        if self.ghost_piece and not self.game_over and not self.is_animating:
            blocks = self.ghost_piece.get_position_blocks()
            for x, y in blocks:
                if y >= 0:  # Only draw if the block is within the visible grid
                    pygame.draw.rect(screen, DARK_GRAY, 
                                   (x * CELL_SIZE + 3, y * CELL_SIZE + 3, 
                                    CELL_SIZE - 6, CELL_SIZE - 6), 1)
        
        # Draw the grid blocks
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    colors = self.grid_colors[y][x]
                    
                    # Skip drawing lines that are being cleared during animation
                    if self.is_animating and y in self.lines_to_clear:
                        # Flash effect during clearing animation
                        if int(self.clear_animation_time * 10) % 2 == 0:
                            pygame.draw.rect(screen, WHITE, 
                                           (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                        continue
                    
                    # Draw block with 3D effect
                    pygame.draw.rect(screen, colors['main'], 
                                   (x * CELL_SIZE + 1, y * CELL_SIZE + 1, 
                                    CELL_SIZE - 2, CELL_SIZE - 2))
                    
                    # Highlight (top and left edges)
                    pygame.draw.line(screen, colors['light'], 
                                   (x * CELL_SIZE + 2, y * CELL_SIZE + 2), 
                                   (x * CELL_SIZE + CELL_SIZE - 3, y * CELL_SIZE + 2), 2)
                    pygame.draw.line(screen, colors['light'], 
                                   (x * CELL_SIZE + 2, y * CELL_SIZE + 2), 
                                   (x * CELL_SIZE + 2, y * CELL_SIZE + CELL_SIZE - 3), 2)
                    
                    # Shadow (bottom and right edges)
                    pygame.draw.line(screen, colors['dark'], 
                                   (x * CELL_SIZE + 2, y * CELL_SIZE + CELL_SIZE - 3), 
                                   (x * CELL_SIZE + CELL_SIZE - 3, y * CELL_SIZE + CELL_SIZE - 3), 2)
                    pygame.draw.line(screen, colors['dark'], 
                                   (x * CELL_SIZE + CELL_SIZE - 3, y * CELL_SIZE + 2), 
                                   (x * CELL_SIZE + CELL_SIZE - 3, y * CELL_SIZE + CELL_SIZE - 3), 2)
        
        # Draw the current piece
        if not self.game_over and not self.is_animating:
            self.current_piece.draw(screen)
        
        # Draw sidebar
        sidebar_x = SCREEN_WIDTH + 10
        
        # Draw game title
        title_text = title_font.render("TETRIS", True, WHITE)
        screen.blit(title_text, (sidebar_x + 30, 20))
        
        # Draw next piece preview
        next_text = font.render("Next Piece:", True, WHITE)
        screen.blit(next_text, (sidebar_x, 80))
        
        # Draw next piece in a nice box
        preview_box = pygame.Rect(sidebar_x, 110, 120, 100)
        pygame.draw.rect(screen, DARK_GRAY, preview_box, 2)
        
        # Center the next piece in the preview box
        next_piece_blocks = self.next_piece.get_position_blocks()
        min_x = min(x for x, _ in next_piece_blocks)
        min_y = min(y for _, y in next_piece_blocks)
        max_x = max(x for x, _ in next_piece_blocks)
        max_y = max(y for _, y in next_piece_blocks)
        
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        
        offset_x = sidebar_x + (120 - width * CELL_SIZE) // 2
        offset_y = 110 + (100 - height * CELL_SIZE) // 2
        
        self.next_piece.draw(screen, 
                           offset_x - self.next_piece.x * CELL_SIZE, 
                           offset_y - self.next_piece.y * CELL_SIZE)
        
        # Draw score and level
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (sidebar_x, 230))
        
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        screen.blit(level_text, (sidebar_x, 260))
        
        lines_text = font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        screen.blit(lines_text, (sidebar_x, 290))
        
        # Draw controls
        controls_y = 350
        controls_text = font.render("Controls:", True, WHITE)
        screen.blit(controls_text, (sidebar_x, controls_y))
        
        controls = [
            "← → : Move",
            "↑ : Rotate",
            "↓ : Soft Drop",
            "Space : Hard Drop",
            "P : Pause"
        ]
        
        for i, control in enumerate(controls):
            ctrl_text = font.render(control, True, WHITE)
            screen.blit(ctrl_text, (sidebar_x, controls_y + 30 + i * 25))
        
        # Draw game over or paused message
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            game_over_text = title_font.render("GAME OVER", True, RED)
            text_width = game_over_text.get_width()
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - text_width // 2, SCREEN_HEIGHT // 2 - 50))
            
            restart_text = font.render("Press R to restart", True, WHITE)
            text_width = restart_text.get_width()
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - text_width // 2, SCREEN_HEIGHT // 2 + 10))
        elif self.paused:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            paused_text = title_font.render("PAUSED", True, YELLOW)
            text_width = paused_text.get_width()
            screen.blit(paused_text, (SCREEN_WIDTH // 2 - text_width // 2, SCREEN_HEIGHT // 2 - 20))

    def reset(self):
        self.__init__()
        # Keep the game in start screen mode when resetting
        self.game_started = False

def main():
    game = TetrisGame()
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                # Start screen controls
                if not game.game_started:
                    if event.key == pygame.K_s:
                        game.game_started = True
                # Game over controls
                elif game.game_over:
                    if event.key == pygame.K_r:
                        game.reset()
                # In-game controls
                else:
                    if event.key == pygame.K_p:
                        game.paused = not game.paused
                    
                    if not game.paused and not game.is_animating:
                        if event.key == pygame.K_LEFT:
                            game.move(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            game.move(1, 0)
                        elif event.key == pygame.K_DOWN:
                            game.move(0, 1)
                        elif event.key == pygame.K_UP:
                            game.rotate_piece()
                        elif event.key == pygame.K_SPACE:
                            game.drop()
        
        game.update(dt)
        
        # Draw everything
        screen.fill(BLACK)
        game.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    main()
    pygame.quit()
