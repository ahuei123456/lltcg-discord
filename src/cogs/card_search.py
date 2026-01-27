import logging

import discord
from discord import app_commands
from discord.ext import commands

from src.db.card_repository import CardData, CardRepository
from src.db.mappings import CHARACTER_MAP, GROUP_MAP, REVERSE_CHAR_MAP, UNIT_MAP

from .views.pagination_view import PaginationView
from .views.start_search_view import StartSearchView
from .views.state import FilterState

_log = logging.getLogger(__name__)


class CardSearch(commands.Cog):
    def __init__(self, bot: commands.Bot, card_repo: CardRepository):
        self.bot = bot
        self.card_repo = card_repo

    async def handle_advanced_search(self, interaction: discord.Interaction, filters: FilterState):
        """Callback for the Advanced Search Dashboard."""
        # Convert state to repo filters
        filter_dict = filters.to_dict()

        # Execute search
        results = self.card_repo.search_cards(filters=filter_dict)
        count = len(results)
        title = f"Search Results: {count} found"
        filters_desc = f"**Filters:**\n{filters.describe_filters()}"

        async def back_to_search_callback(intr: discord.Interaction):
            # Re-launch StartSearchView with current filters
            view = StartSearchView(callback=self.handle_advanced_search, initial_state=filters)
            # Edit original message to show dashboard
            await intr.response.edit_message(content="Advanced Search Dashboard", embed=None, view=view)

        if count > 10:
            # Use Pagination View
            view = PaginationView(
                results=results,
                title=title,
                filters_desc=filters_desc,
                color=discord.Color.green(),
                back_callback=back_to_search_callback,
            )
            # The search button callback already deferred/edited via response.edit_message.
            # So here we must use edit_original_response.
            await interaction.edit_original_response(content=None, embed=view.get_embed(), view=view)
            return

        # <= 10 results, standard display (but with back button?)
        # StartSearchView doesn't have a "Back" button on the embedding itself if we just send an embed.
        # But handle_advanced_search replaces everything.
        # If we want a "Back" button even for small results, we need a View.
        # Let's reuse PaginationView even for small results if we want consistency,
        # or just make a simple View with a Back button.
        # For uniformity, let's use PaginationView but it will just have 1 page.

        view = PaginationView(
            results=results,
            title=title,
            filters_desc=filters_desc,
            color=discord.Color.red() if count == 0 else discord.Color.green(),
            back_callback=back_to_search_callback,
        )
        await interaction.edit_original_response(content=None, embed=view.get_embed(), view=view)

    async def character_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """
        Autocomplete for character names.
        Matches 'current' against English names in REVERSE_CHAR_MAP (values).
        Returns Choice(name="English (Japanese)", value="Japanese").
        """
        current_lower = current.lower()
        matches = []
        # REVERSE_CHAR_MAP: Japanese -> English Title
        # We want to find entries where English Title contains current
        for jp_name, en_name in REVERSE_CHAR_MAP.items():
            if current_lower in en_name.lower():
                # Value is now the Japanese name (jp_name) to pass directly to search_cards
                matches.append(app_commands.Choice(name=f"{en_name} ({jp_name})", value=jp_name))

        # Sort by length of match for better relevance? Or just alphabetical.
        matches.sort(key=lambda x: x.name)
        return matches[:25]

    async def unit_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        """
        Autocomplete for units.
        Matches 'current' against UNIT_MAP keys (lower case English).
        """
        current_lower = current.lower()
        matches = []
        for key, val in UNIT_MAP.items():
            # key is usually lower case English, val is DB Value
            # We show the DB Value (Clean) as name, AND value
            if current_lower in key:
                matches.append(app_commands.Choice(name=val, value=val))

        # Deduplicate by name if multiple keys map to same unit
        unique_matches = []
        seen = set()
        for m in matches:
            if m.name not in seen:
                unique_matches.append(m)
                seen.add(m.name)

        return unique_matches[:25]

    async def group_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """
        Autocomplete for groups.
        """
        # Hardcoded list for cleaner UX given the small set
        # Value is the DB Group Name
        groups = [
            ("μ's", "ラブライブ！"),
            ("Aqours", "ラブライブ！サンシャイン!!"),
            ("Nijigasaki", "ラブライブ！虹ヶ咲学園スクールアイドル同好会"),
            ("Liella!", "ラブライブ！スーパースター!!"),
            ("Hasunosora", "蓮ノ空女学院スクールアイドルクラブ"),
        ]
        return [
            app_commands.Choice(name=name, value=value) for name, value in groups if current.lower() in name.lower()
        ]

    async def rarity_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        # Reuse repo search
        matches = self.card_repo.search_rarity(current)
        return [app_commands.Choice(name=val, value=val) for val in matches]

    def _build_search_result_embed(self, results: list[CardData], filters: dict) -> discord.Embed:
        count = len(results)
        title = f"Search Results: {count} found"

        # Build filter description
        filter_text = []
        if filters.get("query"):
            filter_text.append(f"Query: `{filters['query']}`")
        if filters.get("character"):
            filter_text.append(f"Char: `{filters['character']}`")
        if filters.get("unit"):
            filter_text.append(f"Unit: `{filters['unit']}`")
        if filters.get("group"):
            filter_text.append(f"Group: `{filters['group']}`")
        if filters.get("rarity"):
            filter_text.append(f"Rarity: `{filters['rarity']}`")

        description = "Filters: " + ", ".join(filter_text) + "\n\n"

        if count == 0:
            description += "No cards found matching the criteria."
            color = discord.Color.red()
        else:
            color = discord.Color.green()
            # List first 10
            for i, card in enumerate(results[:10]):
                name = card.get("name", "Unknown")
                rarity = card.get("rarity", "?")
                number = card.get("card_number", "???")
                # Format: [ID] Name (Rarity)
                description += f"`{number}` **{name}** ({rarity})\n"

            if count > 10:
                description += f"\n*...and {count - 10} more.*"

        embed = discord.Embed(title=title, description=description, color=color)
        return embed

    @app_commands.command(name="advanced_search", description="Open the Advanced Search Dashboard")
    async def advanced_search(self, interaction: discord.Interaction):
        """Opens the interactive Advanced Search Dashboard."""
        view = StartSearchView(callback=self.handle_advanced_search)
        await interaction.response.send_message("Launching Advanced Search Dashboard...", view=view, ephemeral=True)

    @app_commands.command(name="search", description="Search for cards with filters")
    @app_commands.autocomplete(
        character=character_autocomplete, unit=unit_autocomplete, group=group_autocomplete, rarity=rarity_autocomplete
    )
    @app_commands.describe(
        query="Text to search in card name",
        character="Character Name",
        unit="Unit Name",
        group="Group Name",
        rarity="Rarity",
    )
    async def search(
        self,
        interaction: discord.Interaction,
        query: str | None = None,
        character: str | None = None,
        unit: str | None = None,
        group: str | None = None,
        rarity: str | None = None,
    ):
        # Check if basic search or advanced dashboard
        if not any([query, character, unit, group, rarity]):
            await interaction.response.send_message(
                "Please provide at least one search filter (Query, Character, Unit, etc.).\n"
                "Use `/advanced_search` to open the interactive dashboard.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        # Normalize inputs from English to Japanese if possible
        # This checks if the input is a known English key, and if so converts it.
        # This handles cases where user types "Honoka" and hits enter without using autocomplete (which sends JP name)

        target_char = character
        if character:
            # Check if it's in our english map
            mapped = CHARACTER_MAP.get(character.lower())
            if mapped:
                target_char = mapped

        target_unit = unit
        if unit:
            mapped = UNIT_MAP.get(unit.lower())
            if mapped:
                target_unit = mapped

        target_group = group
        if group:
            mapped = GROUP_MAP.get(group.lower())
            if mapped:
                target_group = mapped

        results = self.card_repo.search_cards(
            query=query, character=target_char, unit=target_unit, group=target_group, rarity=rarity
        )

        filters = {"query": query, "character": character, "unit": unit, "group": group, "rarity": rarity}

        embed = self._build_search_result_embed(results, filters)
        await interaction.followup.send(embed=embed)
