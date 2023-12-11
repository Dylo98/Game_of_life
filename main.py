import pygame
import numpy as np
import os
import pickle


# Added GameStateManager class that implements the Singleton pattern for game state management
class GameStateManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameStateManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Initialize game state
        self.game_state = np.random.choice([0, 1], size=(n_cells_x, n_cells_y), p=[0.8, 0.2])

    def get_game_state(self):
        return self.game_state

    def set_game_state(self, new_state):
        self.game_state = new_state


# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))

# Grid dimensions
n_cells_x, n_cells_y = 40, 30
cell_width = width // n_cells_x
cell_height = height // n_cells_y

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
gray = (128, 128, 128)
green = (0, 255, 0)

# Button dimensions
button_width, button_height = 200, 50
button_x, button_y = (width - button_width) // 2, height - button_height - 10

# Simulation control variables
running = True
paused = False
tick_interval = 300
last_tick = pygame.time.get_ticks()

# File paths to save
save_file = "game_state.pkl"

# Singleton instance for managing the game state
game_state_manager = GameStateManager()


def draw_button():
    pygame.draw.rect(screen, green, (button_x, button_y, button_width, button_height))
    font = pygame.font.Font(None, 36)
    text = font.render("Next Generation", True, black)
    text_rect = text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
    screen.blit(text, text_rect)


def draw_grid():
    for y in range(0, height, cell_height):
        for x in range(0, width, cell_width):
            cell = pygame.Rect(x, y, cell_width, cell_height)
            pygame.draw.rect(screen, gray, cell, 1)


# Event handling using singleton
def next_generation():
    current_state_next = game_state_manager.get_game_state()
    new_state = np.copy(current_state_next)

    for y in range(n_cells_y):
        for x in range(n_cells_x):
            n_neighbors = current_state_next[(x - 1) % n_cells_x, (y - 1) % n_cells_y] + \
                          current_state_next[x % n_cells_x, (y - 1) % n_cells_y] + \
                          current_state_next[(x + 1) % n_cells_x, (y - 1) % n_cells_y] + \
                          current_state_next[(x - 1) % n_cells_x, y % n_cells_y] + \
                          current_state_next[(x + 1) % n_cells_x, y % n_cells_y] + \
                          current_state_next[(x - 1) % n_cells_x, (y + 1) % n_cells_y] + \
                          current_state_next[x % n_cells_x, (y + 1) % n_cells_y] + \
                          current_state_next[(x + 1) % n_cells_x, (y + 1) % n_cells_y]

            if current_state_next[x, y] == 1 and (n_neighbors < 2 or n_neighbors > 3):
                new_state[x, y] = 0
            elif current_state_next[x, y] == 0 and n_neighbors == 3:
                new_state[x, y] = 1

    game_state_manager.set_game_state(new_state)


def draw_cells():
    current_state_cells = game_state_manager.get_game_state()
    for y in range(n_cells_y):
        for x in range(n_cells_x):
            cell = pygame.Rect(x * cell_width, y * cell_height, cell_width, cell_height)
            if current_state_cells[x, y] == 1:
                pygame.draw.rect(screen, black, cell)


# Implemented write and read logic working with singleton GameStateManager
def save_game_state():
    with open(save_file, 'wb') as file:
        pickle.dump(game_state_manager.get_game_state(), file)


def load_game_state():
    if os.path.exists(save_file):
        with open(save_file, 'rb') as file:
            loaded_state = pickle.load(file)
            game_state_manager.set_game_state(loaded_state)


while running:
    screen.fill(white)
    draw_grid()
    draw_cells()
    draw_button()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if (button_x <= event.pos[0] <= button_x + button_width
                    and button_y <= event.pos[1] <= button_y + button_height):
                next_generation()
            else:
                x, y = event.pos[0] // cell_width, event.pos[1] // cell_height
                current_state = game_state_manager.get_game_state()
                current_state[x, y] = not current_state[x, y]
                game_state_manager.set_game_state(current_state)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_s:
                save_game_state()
            elif event.key == pygame.K_l:
                load_game_state()

    if not paused:
        current_time = pygame.time.get_ticks()
        if current_time - last_tick > tick_interval:
            next_generation()
            last_tick = current_time

pygame.quit()
