# Snake Game with Levels (Python Arcade)

**Module Selected:** Game Framework

## Overview

Classic Snake game built with Python and the Arcade library. The snake grows when it eats food. The player loses if the snake collides with the walls or itself. The game includes multiple difficulty levels, pause/restart controls, save/load support, and optional sound effects.

## Features

- Display graphics (grid-based field, snake, food)
- Keyboard input: arrow keys, `SPACE` pause, `ENTER` restart, `ESC` quit
- Moveable objects implemented via a tick-based movement model
- Levels that change difficulty (speed increases at score thresholds)
- Save/Load game state (simple JSON file)
- Optional sound effects and music (use `assets/` for audio files)

## Requirements mapping

- Graphics: implemented with Arcade drawing and sprites
- Input: handled by Arcade `on_key_press`
- Movement: controlled by a movement tick separate from rendering
- Additional requirement satisfied: Levels that change difficulty

## Install

Requires Python 3.14+ (or Python 3.11+) and the `arcade` library.

```powershell
py -m pip install -r requirements.txt
```

## Run

```powershell
py snake_game.py
```

## Controls

- Arrow keys: Move snake
- SPACE: Pause / Unpause
- ENTER: Restart after Game Over
- ESC: Quit game
- S: Save game state to `save_slot.json`
- L: Load game state from `save_slot.json`

## Files

- `snake_game.py` — main game implementation
- `requirements.txt` — required packages
- `assets/` — put sound files here (see `assets/README.md`)
- `save_slot.json` — optional save file created at runtime
- `highscore.json` — persistent high score storage

## Notes

- The implementation uses a grid-based system to simplify collisions and placement.
- Movement updates run at a configurable ticks-per-second (moves/sec) controlled by level.
- Rendering runs at Arcade's frame rate (default 60 FPS) so visuals remain smooth.
