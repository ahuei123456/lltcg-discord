from unittest.mock import AsyncMock, MagicMock

import pytest

from src.cogs.card_search import CardSearch


@pytest.fixture
def search_cog():
    bot = MagicMock()
    card_repo = MagicMock()
    # Mock search_rarity for autocomplete
    card_repo.search_rarity.return_value = ["L+", "SR"]
    return CardSearch(bot, card_repo)


@pytest.mark.asyncio
async def test_keyword_autocomplete_character(search_cog):
    # Test "Honoka" -> matches Character
    interaction = MagicMock()
    choices = await search_cog.keyword_autocomplete(interaction, "Honoka")

    # Expect "Char: Kousaka Honoka" -> value "高坂穂乃果"
    found = any("Honoka" in c.name and c.value == "高坂穂乃果" for c in choices)
    assert found


@pytest.mark.asyncio
async def test_keyword_autocomplete_unit(search_cog):
    # Test "Printemps" -> matches Unit
    interaction = MagicMock()
    choices = await search_cog.keyword_autocomplete(interaction, "Prin")

    found = any("Unit: Printemps" in c.name and c.value == "Printemps" for c in choices)
    assert found


@pytest.mark.asyncio
async def test_keyword_autocomplete_group(search_cog):
    # Test "Aquors" -> matches Group (Wait, input "Aqours", map key "Aqours")
    interaction = MagicMock()
    choices = await search_cog.keyword_autocomplete(interaction, "Aqou")

    found = any("Group: Aqours" in c.name and c.value == "ラブライブ！サンシャイン!!" for c in choices)
    assert found


@pytest.mark.asyncio
async def test_search_command_flow(search_cog):
    interaction = MagicMock()
    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()
    interaction.edit_original_response = AsyncMock()
    interaction.response.is_done.return_value = True  # Simulate deferred

    search_cog.card_repo.search_cards.return_value = []

    # Call search with some filters
    await search_cog.search.callback(
        search_cog, interaction, keyword="Test", cost="4+", heart_color="Red", heart_count="2"
    )

    interaction.response.defer.assert_called_once()

    # Check repo call
    args, kwargs = search_cog.card_repo.search_cards.call_args
    filters = kwargs["filters"]

    assert filters["keyword"] == "Test"
    assert filters["cost_min"] == 4  # 4+ parsed
    assert filters["hearts"]["heart02"] == "2"  # Red -> heart02

    # Check display called (edit_original_response since deferred)
    interaction.edit_original_response.assert_called_once()


@pytest.mark.asyncio
async def test_search_invalid_cost(search_cog):
    interaction = MagicMock()
    interaction.response.defer = AsyncMock()

    from src.utils.errors import InvalidLookupArgsError

    with pytest.raises(InvalidLookupArgsError):
        await search_cog.search.callback(search_cog, interaction, cost="invalid")
