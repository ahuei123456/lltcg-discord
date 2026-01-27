# lltcg-discord
A utility bot for LLOCG data

## Usage

To run the bot, use the following command:

```
uv run python -m src.main
```
## Commands

### `/card`
Look up card details by Series, Product, Number, and Rarity.

**Usage**:
`/card series:PL!N product:bp4 number:32 rarity:L+`

- **series**: Card Series (e.g., `PL!N`) - *Autocomplete enabled*
- **product**: Product Code (e.g., `bp4`) - *Autocomplete enabled*
- **number**: Card Number (e.g., `32`) - *Integer input (auto-padded to 3 digits)*
- **rarity**: Rarity (e.g., `L+`) - *Autocomplete enabled*

### `/search`
Quickly find cards using specific filters.
**Usage**: `/search query:love live` or `/search character:Honoka`
- Requires at least one argument.
- If no arguments are provided, prompts to use `/advanced_search`.

### `/advanced_search`
Opens the interactive **Advanced Search Dashboard**.
- **Features**:
    - Filter by Card Type (Member/Live).
    - Numeric ranges for Cost and Blades.
    - Complex Heart requirements (e.g., "Any 2 Pink Hearts").
    - Blade Heart matching (OR logic).
    - Pagination for large result sets.

## Features

- **Rich Embeds**: Visual card data including images, cost, score, unit, and group.
- **Emoji System**: Automatic mapping of heart symbols in stats and ability text.
- **Optimized Search**: Pre-sorted indices for lightning-fast autocomplete.
- **Smart ID Handling**: Fullwidth character normalization and auto-padding for card numbers.

## Configuration

Create a `config.json` file in the root directory:

```json
{
    "DISCORD_TOKEN": "your_bot_token",
    "GUILDS": [1234567890],
    "CARD_DATA_PATH": "data/card_data.json",
    "IMAGE_CACHE_PATH": "data/images"
}
```

## Deployment

The bot is containerized with Docker for easy deployment to AWS Lightsail or any other VPS.

Detailed instructions can be found in [deployment.md](docs/deployment.md).

Quick start (Linux/macOS):
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## Testing

This project uses `pytest` for unit testing, specifically for the emoji mapping and card lookup logic.

Run tests:
```bash
uv run pytest
```

## Development

This project uses `uv` for dependency management and `pre-commit` for code quality.

### Setup

```bash
uv sync
uv run pre-commit install
```
