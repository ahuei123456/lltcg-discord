import argparse
import logging
import sys

import discord
from discord.ext import commands

from src import config
from src.cogs.card_lookup import CardLookup
from src.db.card_repository import CardRepository

_log = logging.getLogger(__name__)


class LLTCGBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        settings = config.get_config()

        # Initialize Repository
        card_repo = CardRepository(settings["CARD_DATA_PATH"])
        card_repo.load_data()

        # Load Cogs
        await self.add_cog(CardLookup(self, card_repo))

        _log.info("Initial data loaded and Cog added.")

        # Sync commands
        # Note: In production, syncing globally can take up to an hour.
        # Syncing to specific guilds is instant for testing.
        for guild_id in settings["GUILDS"]:
            guild = discord.Object(id=guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        _log.info("Commands synced.")


client = LLTCGBot()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LLTCG Bot")
    parser.add_argument("--config-path", type=str, default="config.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        # Explicitly load the configuration ONCE at startup
        config.load_config(args.config_path)
    except config.ConfigError as e:
        _log.error(f"Fatal Error: Failed to load configuration - {e}")
        sys.exit(1)

    # Now access the config via the accessor function
    settings = config.get_config()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(logging.WARNING)  # Reduce discord lib noise

    # Validate config before running
    if not settings["DISCORD_TOKEN"]:
        _log.critical("DISCORD_TOKEN is not set")
    elif not settings["GUILDS"]:
        _log.critical("GUILDS is not set")
    elif not settings["CARD_DATA_PATH"]:
        _log.critical("CARD_DATA_PATH is not set")
    else:
        try:
            client.run(settings["DISCORD_TOKEN"], log_handler=None)  # Use basicConfig handler
        except Exception as e:
            _log.exception(f"Fatal error running bot: {e}")
