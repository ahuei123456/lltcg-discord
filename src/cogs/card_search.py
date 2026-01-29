import logging
from collections.abc import Callable
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

from src.db.card_repository import CardData, CardRepository
from src.db.mappings import GROUP_MAP, REVERSE_CHAR_MAP, UNIT_MAP
from src.utils.errors import InvalidLookupArgsError
from src.utils.parsing import parse_range_string

from .views.pagination_view import PaginationView
from .views.start_search_view import StartSearchView
from .views.state import FilterState

_log = logging.getLogger(__name__)

COLOR_MAP = {
    "Pink": "heart01",
    "Red": "heart02",
    "Yellow": "heart03",
    "Green": "heart04",
    "Blue": "heart05",
    "Purple": "heart06",
}


class CardSearch(commands.Cog):
    def __init__(self, bot: commands.Bot, card_repo: CardRepository):
        self.bot = bot
        self.card_repo = card_repo

    async def _display_results(
        self,
        interaction: discord.Interaction,
        results: list[CardData],
        filters_desc: str,
        back_callback: Callable | None = None,
    ):
        """Helper to display search results using PaginationView."""
        count = len(results)
        title = f"Search Results: {count} found"

        # Determine color based on results
        color = discord.Color.red() if count == 0 else discord.Color.green()

        # Even for 0 or small results, we use PaginationView for consistency
        # (and to support "Back" if provided, though typically disabled for CLI)
        view = PaginationView(
            results=results, title=title, filters_desc=filters_desc, color=color, back_callback=back_callback
        )

        # If interaction was deferred, use edit_original_response
        if interaction.response.is_done():
            await interaction.edit_original_response(content=None, embed=view.get_embed(), view=view)
        else:
            await interaction.response.send_message(embed=view.get_embed(), view=view)

    async def handle_advanced_search(self, interaction: discord.Interaction, filters: FilterState):
        """Callback for the Advanced Search Dashboard."""
        filter_dict = filters.to_dict()
        results = self.card_repo.search_cards(filters=filter_dict)

        async def back_to_search_callback(intr: discord.Interaction):
            view = StartSearchView(callback=self.handle_advanced_search, initial_state=filters)
            await intr.response.edit_message(content="Advanced Search Dashboard", embed=None, view=view)

        await self._display_results(
            interaction,
            results,
            filters_desc=f"**Filters:**\n{filters.describe_filters()}",
            back_callback=back_to_search_callback,
        )

    # --- Autocomplete Solvers ---

    async def keyword_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """
        Autocomplete for 'keyword' argument.
        Matches English input against Characters, Units, and Groups.
        Returns Japanese values.
        """
        current_lower = current.lower()
        matches = []

        # 1. Characters (REVERSE_CHAR_MAP: Japanese -> English)
        for jp_val, en_name in REVERSE_CHAR_MAP.items():
            if current_lower in en_name.lower():
                matches.append(app_commands.Choice(name=f"Char: {en_name}", value=jp_val))

        # 2. Units (UNIT_MAP: English -> Japanese)
        for en_name, jp_val in UNIT_MAP.items():
            if current_lower in en_name.lower():
                # Use the DB value (jp_val) for display as it is properly capitalized (e.g. "Printemps")
                matches.append(app_commands.Choice(name=f"Unit: {jp_val}", value=jp_val))

        # 3. Groups (GROUP_MAP: English -> Japanese)
        for en_name, jp_val in GROUP_MAP.items():
            if current_lower in en_name.lower():
                # Capitalize key for display since value is Japanese
                matches.append(app_commands.Choice(name=f"Group: {en_name.title()}", value=jp_val))

        # Deduplicate matches by value
        seen = set()
        unique_matches = []
        for m in matches:
            if m.value not in seen:
                unique_matches.append(m)
                seen.add(m.value)

        # Sort matches (Exact matches first could be nice, currently alphabetical by name label)
        # Verify limit
        return unique_matches[:25]

    async def rarity_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        matches = self.card_repo.search_rarity(current)
        return [app_commands.Choice(name=val, value=val) for val in matches]

    # --- Commands ---

    @app_commands.command(name="advanced_search", description="Open the Advanced Search Dashboard")
    async def advanced_search(self, interaction: discord.Interaction):
        view = StartSearchView(callback=self.handle_advanced_search)
        await interaction.response.send_message("Launching Advanced Search Dashboard...", view=view, ephemeral=True)

    @app_commands.command(name="search", description="Search for cards. Default: Keyword search.")
    @app_commands.describe(
        keyword="Search by Name, Unit, or Group",
        card_type="Member or Live",
        cost="Cost (e.g. 4, 2-4, 4+, <4)",
        heart_color="Required heart color filter",
        heart_count="Count for heart color (e.g. 2, 2+). Ignored if color not set.",
        blade_heart="Blade Heart of the card",
        blades="# of blades on the card",
        rarity="Card Rarity",
    )
    @app_commands.choices(
        card_type=[
            app_commands.Choice(name="Member", value="メンバー"),
            app_commands.Choice(name="Live", value="ライブ"),
        ],
        heart_color=[app_commands.Choice(name=k, value=k) for k in COLOR_MAP],
        blade_heart=[
            app_commands.Choice(name="All", value="ALL"),
            app_commands.Choice(name="Score", value="Score"),
            app_commands.Choice(name="Draw", value="Draw"),
            # Add Colors to Blade Heart choices if desired, or simplified list
            app_commands.Choice(name="Pink", value="heart01"),
            app_commands.Choice(name="Red", value="heart02"),
            app_commands.Choice(name="Yellow", value="heart03"),
            app_commands.Choice(name="Green", value="heart04"),
            app_commands.Choice(name="Blue", value="heart05"),
            app_commands.Choice(name="Purple", value="heart06"),
        ],
    )
    @app_commands.autocomplete(keyword=keyword_autocomplete, rarity=rarity_autocomplete)
    async def search(
        self,
        interaction: discord.Interaction,
        keyword: str | None = None,
        card_type: str | None = None,
        cost: str | None = None,
        heart_color: str | None = None,
        heart_count: str | None = None,
        blade_heart: str | None = None,
        blades: str | None = None,
        rarity: str | None = None,
    ):
        await interaction.response.defer()

        filters: dict[str, Any] = {}

        if keyword:
            filters["keyword"] = keyword

        if card_type:
            filters["card_type"] = card_type

        if rarity:
            filters["rarity"] = rarity

        # Parse Cost
        if cost:
            min_c, max_c = parse_range_string(cost)
            if min_c is None and max_c is None:
                raise InvalidLookupArgsError(f"Invalid cost format: {cost}")
            if min_c is not None:
                filters["cost_min"] = min_c
            if max_c is not None:
                filters["cost_max"] = max_c

        # Parse Blades
        if blades:
            min_b, max_b = parse_range_string(blades)
            if min_b is None and max_b is None:
                raise InvalidLookupArgsError(f"Invalid blades format: {blades}")
            if min_b is not None:
                filters["blades_min"] = min_b
            if max_b is not None:
                filters["blades_max"] = max_b

        # Heart Logic
        if heart_color:
            # Map "Pink" -> "heart01"
            db_key = COLOR_MAP.get(heart_color)
            if db_key:
                val_expr = heart_count if heart_count else "1"  # Default to 1 if no count provided? Or 1+?
                filters.setdefault("hearts", {})[db_key] = val_expr
        elif heart_count:
            # Warning: heart_count ignored without color
            # We could send a ephemeral warning but we are deferred?
            # Ideally just ignore or append to description.
            pass

        # Blade Heart Logic
        if blade_heart:
            # If "ALL", "Score", "Draw" -> simple map
            # If "Pink" -> "heart01"
            # DB keys: "ALL1", "Score", "Draw" (requires mapping from "Score" -> "Score"?)

            # Helper map for blade hearts specifically (or reuse state logic)
            # Standardizing:
            if blade_heart == "ALL":
                filters["blade_hearts"] = ["ALL1", "ALL2"]  # Search both generic alls?
            elif blade_heart == "Score":
                filters["blade_hearts"] = ["Score"]
            elif blade_heart == "Draw":
                filters["blade_hearts"] = ["Draw"]
            else:
                # It's a color key from choices (e.g. heart01) or a color name?
                # Choices used values like heart01.
                filters["blade_hearts"] = [blade_heart]

        # Prepare filters
        filters["keyword"] = keyword
        filters["card_type"] = card_type
        # ... logic above already populates filters dict ...

        # filters variable is already accurate from above logic
        results = self.card_repo.search_cards(filters=filters)

        # Describe filters for display
        desc_parts = []
        if keyword:
            desc_parts.append(f"Keyword: `{keyword}`")
        if card_type:
            desc_parts.append(f"Type: `{card_type}`")
        if cost:
            desc_parts.append(f"Cost: `{cost}`")
        if heart_color:
            desc_parts.append(f"Heart: `{heart_color}` ({heart_count or '1'})")
        if blade_heart:
            desc_parts.append(f"Blade Heart: `{blade_heart}`")
        if blades:
            desc_parts.append(f"Blades: `{blades}`")
        if rarity:
            desc_parts.append(f"Rarity: `{rarity}`")

        filters_desc = "**Filters:**\n" + ", ".join(desc_parts)

        await self._display_results(interaction, results, filters_desc)
