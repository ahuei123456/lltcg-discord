# Project: LLTCG Discord Bot

## Architecture
- **Framework**: `discord.py` (Version 2.0+) using Cogs extensions.
- **Dependency Manager**: `uv`.
- **Entry Point**: `src.main` (Run via `uv run python -m src.main`).
- **Bot Class**: `src.bot.LLTCGBot` (Subclass of `commands.Bot`).

## Domain Knowledge: Card Data
- **Source**: `data/card_data.json`.
- **ID Format**: `Series-Product-Number-Rarity` (e.g., `PL!N-bp4-032-L+`).
    - **Series**: String (e.g., `PL!N`).
    - **Product**: String (e.g., `bp4`).
    - **Number**: 3-digit zero-padded integer (e.g., `032`).
    - **Rarity**: String (e.g., `L+`).
- **Normalization Rules**:
    - **Rarity**: Fullwidth `＋` is converted to ASCII `+`.
    - **Number**: Input integers are auto-padded to 3 digits (e.g., `32` input -> lookup `032`).

## Key Components
- **Repository** (`src/db/card_repository.py`):
    - Loads JSON data into memory.
    - Maintains pre-sorted lists for valid IDs to optimize autocomplete.
- **Lookup Cog** (`src/cogs/card_lookup.py`):
    - Implements `/card` slash command.
    - Handles autocomplete (Series/Product/Rarity) and validation.
    - **Visuals**: Features a rich emoji system for required/blade hearts.
    - **Logic**: Uses single-pass regex replacement in ability text to swap keywords for emojis without nesting errors.
    - **Refinement**: Merges `blade_hearts` (dict) and `special_hearts` (string) into a single unified display.

## Configuration
- **File**: `config.json` in root.
- **Required Keys**:
    - `DISCORD_TOKEN`: Bot token.
    - `GUILDS`: List of integer Guild IDs for testing/sync.
    - `CARD_DATA_PATH`: Path to the JSON data file.

## Development Workflow
- **Linting**: `uv run ruff check . --fix`
- **Type Checking**: `uv run mypy .`
- **Pre-commit**: `uv run pre-commit run --all-files` (Runs both ruff and mypy).
