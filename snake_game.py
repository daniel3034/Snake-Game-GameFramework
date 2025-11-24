"""Snake Game with Levels

Run: python snake_game.py

Controls:
  Arrow keys: move
  SPACE: pause/unpause
  ENTER: restart after game over
  ESC: quit
  S: save
  L: load

This implementation uses a grid and tick-based movement so rendering stays smooth at 60 FPS
while the game logic advances at `moves_per_second` set by the current level.
"""
import arcade
import arcade.draw
import random
import json
import os
from typing import List, Tuple

# Configuration
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT
SCREEN_TITLE = "Snake Game with Levels"

SAVE_FILE = "save_slot.json"
HIGHSCORE_FILE = "highscore.json"

Pos = Tuple[int, int]

LEVELS = [
    {"score": 0,   "speed": 5},   # Level 1
    {"score": 50,  "speed": 8},   # Level 2
    {"score": 100, "speed": 12},  # Level 3
    {"score": 150, "speed": 15},  # Level 4
]


class SnakeGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.AMAZON)
        self.asset_path = os.path.join(os.path.dirname(__file__), "assets")
        self._load_sounds()
        self.reset_game()

    def _load_sounds(self):
        # Attempt to load sounds; missing files are allowed
        def load(name):
            path = os.path.join(self.asset_path, name)
            try:
                return arcade.load_sound(path)
            except Exception:
                return None

        self.sound_eat = load("eat.wav")
        self.sound_level = load("levelup.wav")
        self.sound_gameover = load("gameover.wav")
        self.sound_bgm = load("bgm.ogg") or load("bgm.mp3")

    def reset_game(self):
        # Start with a single-segment snake in the center
        self.snake: List[Pos] = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction: Pos = (1, 0)
        self.spawn_food()
        self.score = 0
        self.level_index = 0
        self.moves_per_second = LEVELS[self.level_index]["speed"]
        self.tick_accumulator = 0.0
        self.game_over = False
        self.paused = False
        self.load_highscore()

    def spawn_food(self):
        # Place food on a random free grid cell
        while True:
            p = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if p not in self.snake:
                self.food = p
                return

    def on_draw(self):
        self.clear()
        # Draw checkerboard grid
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                color = arcade.color.DARK_SLATE_GRAY if (x + y) % 2 == 0 else arcade.color.DIM_GRAY
                arcade.draw.draw_lrbt_rectangle_filled(
                    x * CELL_SIZE,
                    (x + 1) * CELL_SIZE - 1,
                    y * CELL_SIZE,
                    (y + 1) * CELL_SIZE - 1,
                    color,
                )

        # Draw food
        fx, fy = self.food
        arcade.draw.draw_circle_filled(fx * CELL_SIZE + CELL_SIZE / 2, fy * CELL_SIZE + CELL_SIZE / 2, CELL_SIZE // 2 - 2, arcade.color.RED)

        # Draw snake segments
        for i, (sx, sy) in enumerate(self.snake):
            color = arcade.color.GREEN if i == 0 else arcade.color.DARK_GREEN
            arcade.draw.draw_lrbt_rectangle_filled(sx * CELL_SIZE, (sx + 1) * CELL_SIZE - 2, sy * CELL_SIZE, (sy + 1) * CELL_SIZE - 2, color)

        # HUD
        arcade.draw_text(f"Score: {self.score}", 10, SCREEN_HEIGHT - 22, arcade.color.WHITE, 14)
        arcade.draw_text(f"Level: {self.level_index + 1}", 150, SCREEN_HEIGHT - 22, arcade.color.WHITE, 14)
        arcade.draw_text(f"High: {self.highscore}", 280, SCREEN_HEIGHT - 22, arcade.color.WHITE, 14)

        if self.paused:
            arcade.draw_text("Paused", SCREEN_WIDTH / 2 - 40, SCREEN_HEIGHT / 2, arcade.color.YELLOW, 24)

        if self.game_over:
            arcade.draw_text("GAME OVER - Press ENTER to restart", SCREEN_WIDTH / 2 - 180, SCREEN_HEIGHT / 2, arcade.color.RED, 18)

    def on_key_press(self, key, modifiers):
        # Change direction (prevent immediate 180-degree turn)
        if key == arcade.key.UP and self.direction != (0, -1):
            self.direction = (0, 1)
        elif key == arcade.key.DOWN and self.direction != (0, 1):
            self.direction = (0, -1)
        elif key == arcade.key.LEFT and self.direction != (1, 0):
            self.direction = (-1, 0)
        elif key == arcade.key.RIGHT and self.direction != (-1, 0):
            self.direction = (1, 0)
        elif key == arcade.key.SPACE:
            self.paused = not self.paused
        elif key == arcade.key.ENTER and self.game_over:
            self.reset_game()
        elif key == arcade.key.ESCAPE:
            arcade.close_window()
        elif key == arcade.key.S:
            self.save_game()
        elif key == arcade.key.L:
            self.load_game()

    def on_update(self, delta_time: float):
        if self.paused or self.game_over:
            return
        self.tick_accumulator += delta_time
        tick_interval = 1.0 / self.moves_per_second
        while self.tick_accumulator >= tick_interval:
            self.tick_accumulator -= tick_interval
            self.game_tick()

    def game_tick(self):
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Check collisions
        hx, hy = new_head
        if hx < 0 or hx >= GRID_WIDTH or hy < 0 or hy >= GRID_HEIGHT or new_head in self.snake:
            self.game_over = True
            self._maybe_play(self.sound_gameover)
            self.save_highscore()
            return

        # Move snake: insert new head
        self.snake.insert(0, new_head)

        # Check for food
        if new_head == self.food:
            self.score += 10
            self._maybe_play(self.sound_eat)
            self.spawn_food()
            self.check_level_up()
        else:
            self.snake.pop()

    def check_level_up(self):
        # Find highest level matching the current score
        for idx in reversed(range(len(LEVELS))):
            if self.score >= LEVELS[idx]["score"]:
                if idx != self.level_index:
                    self.level_index = idx
                    self.moves_per_second = LEVELS[idx]["speed"]
                    self._maybe_play(self.sound_level)
                break

    def _maybe_play(self, sound):
        try:
            if sound:
                arcade.play_sound(sound)
        except Exception:
            pass

    def save_game(self):
        data = {
            "snake": self.snake,
            "direction": self.direction,
            "food": self.food,
            "score": self.score,
            "level_index": self.level_index,
        }
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(data, f)
            print("Game saved.")
        except Exception as e:
            print("Failed to save:", e)

    def load_game(self):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
            self.snake = [tuple(p) for p in data["snake"]]
            self.direction = tuple(data["direction"])
            self.food = tuple(data["food"])
            self.score = data["score"]
            self.level_index = data["level_index"]
            self.moves_per_second = LEVELS[self.level_index]["speed"]
            self.game_over = False
            self.paused = False
            print("Game loaded.")
        except Exception as e:
            print("Failed to load:", e)

    def save_highscore(self):
        try:
            data = {"highscore": max(self.highscore, self.score)}
            with open(HIGHSCORE_FILE, "w") as f:
                json.dump(data, f)
            self.highscore = data["highscore"]
        except Exception:
            pass

    def load_highscore(self):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                data = json.load(f)
            self.highscore = data.get("highscore", 0)
        except Exception:
            self.highscore = 0


if __name__ == "__main__":
    try:
        game = SnakeGame()
        arcade.run()
    except Exception as e:
        print("Error starting game. Make sure 'arcade' is installed:")
        print("pip install -r requirements.txt")
        print(e)
