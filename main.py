import pygame
import random
from pathlib import Path
import sys

# ---------------- CONFIG ----------------
GRID_SIZE = 20            # number of cells in x and y
CELL_SIZE = 20            # pixels per cell
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 10                  # base frames per second
LEVEL_UP_SCORE = 5        # points to reach next level
HIGH_SCORE_FILE = Path("highscore.txt")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GREEN = (0, 180, 0)
DARK_GREEN = (0, 120, 0)
GRAY = (50, 50, 50)
YELLOW = (255, 215, 0)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# ---------------- HELPER FUNCTIONS ----------------
def load_highscore():
    if HIGH_SCORE_FILE.exists():
        try:
            return int(HIGH_SCORE_FILE.read_text().strip())
        except:
            return 0
    return 0

def save_highscore(score):
    try:
        HIGH_SCORE_FILE.write_text(str(score))
    except:
        pass

# ---------------- GAME CLASS ----------------
class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game with Levels & Obstacles")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.large_font = pygame.font.SysFont(None, 48)
        self.reset_game()
    
    def reset_game(self):
        self.snake = [(GRID_SIZE//2, GRID_SIZE//2)]
        self.direction = UP
        self.score = 0
        self.level = 1
        self.speed = FPS
        self.obstacles = []
        self.generate_obstacles()
        self.food = self.random_free_cell()
        self.highscore = load_highscore()
        self.game_over_flag = False
    
    def generate_obstacles(self):
        self.obstacles = []
        num_obstacles = (self.level - 1) * 3  # increase obstacles each level
        while len(self.obstacles) < num_obstacles:
            cell = self.random_free_cell()
            if cell not in self.obstacles:
                self.obstacles.append(cell)

    def random_free_cell(self):
        while True:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            cell = (x, y)
            if cell not in self.snake and cell not in self.obstacles:
                return cell

    def move_snake(self):
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Check deadly walls
        if not (0 <= new_head[0] < GRID_SIZE and 0 <= new_head[1] < GRID_SIZE):
            self.game_over()
            return

        # Check obstacles
        if new_head in self.obstacles:
            self.game_over()
            return

        # Check self collision
        if new_head in self.snake:
            self.game_over()
            return

        # Move snake
        self.snake = [new_head] + self.snake[:-1]

        # Check food collision
        if new_head == self.food:
            self.snake.append(self.snake[-1])  # grow snake
            self.score += 1
            if self.score > self.highscore:
                self.highscore = self.score
            self.food = self.random_free_cell()

            # Level up
            if self.score % LEVEL_UP_SCORE == 0:
                self.level += 1
                self.speed += 2
                self.generate_obstacles()

    def change_direction(self, new_dir):
        # prevent reversing
        opposite = (-self.direction[0], -self.direction[1])
        if new_dir != opposite:
            self.direction = new_dir

    def game_over(self):
        save_highscore(self.highscore)
        self.game_over_flag = True

    def draw_grid(self):
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (x,0),(x,WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (0,y),(WINDOW_WIDTH,y))

    def draw_snake(self):
        for i, (x, y) in enumerate(self.snake):
            color = GREEN if i == 0 else DARK_GREEN
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, color, rect)

    def draw_food(self):
        x, y = self.food
        rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, RED, rect)

    def draw_obstacles(self):
        for (x, y) in self.obstacles:
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, YELLOW, rect)

    def draw_info(self):
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        high_text = self.font.render(f"High Score: {self.highscore}", True, WHITE)
        self.screen.blit(score_text, (5,5))
        self.screen.blit(level_text, (5,25))
        self.screen.blit(high_text, (5,45))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_highscore(self.highscore)
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        self.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.change_direction(RIGHT)
                    elif event.key == pygame.K_r and self.game_over_flag:
                        self.reset_game()

            if not self.game_over_flag:
                self.move_snake()

            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_snake()
            self.draw_food()
            self.draw_obstacles()
            self.draw_info()

            if self.game_over_flag:
                over_text = self.large_font.render("GAME OVER", True, RED)
                self.screen.blit(over_text, (WINDOW_WIDTH//2 - over_text.get_width()//2, WINDOW_HEIGHT//2 - 30))
                restart_text = self.font.render("Press R to Restart", True, WHITE)
                self.screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//2 + 20))

            pygame.display.flip()
            self.clock.tick(self.speed)

# ---------------- RUN GAME ----------------
if __name__ == "__main__":
    game = SnakeGame()
    game.run()
