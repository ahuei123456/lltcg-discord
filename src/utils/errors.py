import logging

from discord import app_commands


class BotCommandError(app_commands.AppCommandError):
    """Base class for custom command errors specific to this bot."""

    log_level: int = logging.INFO

    def __init__(self, message: str):
        super().__init__(message)


class InvalidLookupArgsError(BotCommandError):
    """Raised when command arguments for lookup/search are invalid."""

    def __init__(self, message: str = "Invalid arguments provided."):
        super().__init__(f"❌ {message}")


class NoSearchResultsError(BotCommandError):
    """Raised when a search yields no results."""

    def __init__(self):
        super().__init__("❌ No cards found matching your criteria.")
