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
Quickly find cards using specific filters directly from the chat.

**Arguments**:
- `keyword`: Searches Name, Unit, and Group (OR logic). *Autocomplete enabled*.
- `cost`: Filter by cost (e.g., `2`, `2-4`, `4+`, `<3`).
- `blades`: Filter by blades (e.g., `1`, `1+`).
- `heart_color`: Filter by required heart color (e.g., `Red`).
- `heart_count`: Count for the heart color (e.g., `2`, `2+`).
- `blade_heart`: Filter by blade heart symbols (e.g., `Score`, `Draw`, `Pink`).
- `rarity`: Filter by rarity.

**Usage Examples**:
- Find Honoka cards with cost 2 or less: `/search keyword:Honoka cost:<3`
- Find cards requiring 2 Red hearts: `/search heart_color:Red heart_count:2`
- Find Score triggers: `/search blade_heart:Score`

**Note**: If no arguments are provided, it launches the **/advanced_search** dashboard.

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
