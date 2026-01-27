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
    - **Refactor**: Split into modular helpers (`_build_card_embed`, `_get_or_download_image`, `_apply_ability_emojis`) for better maintainability.
    - **Image Handling**: Automatically downloads and caches card images locally to `IMAGE_CACHE_PATH`.
    - **Emoji Logic**: Uses a single-pass regex to replace keywords in ability text.
        - **Literal Matches**: Bracketed terms like `[桃ブレード]` (Japanese colors).
        - **Boundary Matches**: Keywords like `E`, `ブレード`, `ハート`, and `ALLブレード` only match when surrounded by spaces (standalone icons).
    - **Refinement**: Merges `blade_hearts` (dict) and `special_hearts` (string) into a single unified display.

## Configuration
- **File**: `config.json` in root.
- **Required Keys**:
    - `DISCORD_TOKEN`: Bot token.
    - `GUILDS`: List of integer Guild IDs for testing/sync.
    - `CARD_DATA_PATH`: Path to the JSON data file.
    - `IMAGE_CACHE_PATH`: Directory for locally cached card images.

## Deployment
- **Containerization**: Docker multi-stage build using `uv` for minimal image size.
- **Automation**: `scripts/deploy.sh` handles pulling code, building, and replacing the container.
- **Hosting**: Optimized for AWS Lightsail (Ubuntu) with volumes for `config.json`, `card_data.json`, and the image cache.

## Development Workflow
- **Linting**: `uv run ruff check . --fix`
- **Type Checking**: `uv run mypy .`
- **Testing**: `uv run pytest` (Comprehensive suite for emoji logic in `tests/`).
- **Pre-commit**: `uv run pre-commit run --all-files` (Runs both ruff and mypy).
