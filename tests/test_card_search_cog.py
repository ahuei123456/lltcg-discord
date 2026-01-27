from unittest.mock import MagicMock

import pytest

from src.cogs.card_search import CardSearch


@pytest.fixture
def search_cog():
    bot = MagicMock()
    card_repo = MagicMock()
    return CardSearch(bot, card_repo)


@pytest.mark.asyncio
async def test_character_autocomplete(search_cog):
    # Test input "Honoka"
    interaction = MagicMock()
    choices = await search_cog.character_autocomplete(interaction, "Honoka")

    # Should find at least "Honoka (高坂穂乃果)" -> value="高坂穂乃果"
    assert len(choices) > 0
    # Check if correct choice exists
    found = any(c.name == "Honoka (高坂穂乃果)" and c.value == "高坂穂乃果" for c in choices)
    assert found


@pytest.mark.asyncio
async def test_character_autocomplete_lowercase(search_cog):
    # Test input "honoka"
    interaction = MagicMock()
    choices = await search_cog.character_autocomplete(interaction, "honoka")
    found = any(c.value == "高坂穂乃果" for c in choices)
    assert found


@pytest.mark.asyncio
async def test_unit_autocomplete(search_cog):
    # Test input "printemps"
    interaction = MagicMock()
    choices = await search_cog.unit_autocomplete(interaction, "printemps")

    # Should find "Printemps" -> value "Printemps" (DB Value)
    found = any(c.name == "Printemps" and c.value == "Printemps" for c in choices)
    assert found


@pytest.mark.asyncio
async def test_group_autocomplete(search_cog):
    # Test input "ni" -> Nijigasaki
    interaction = MagicMock()
    choices = await search_cog.group_autocomplete(interaction, "ni")

    # Name: "Nijigasaki", Value: "ラブライブ！虹ヶ咲学園スクールアイドル同好会"
    found = any(c.name == "Nijigasaki" and c.value == "ラブライブ！虹ヶ咲学園スクールアイドル同好会" for c in choices)
    assert found


@pytest.mark.asyncio
async def test_search_no_args(search_cog):
    interaction = MagicMock()
    # Mock response to be async
    interaction.response.send_message = MagicMock()

    # helper for async mocks if needed, but MagicMock returns MagicMock which is awaitable if configured?
    # standard MagicMock isn't awaitable. We need AsyncMock.
    # unittest.mock.AsyncMock is available in Python 3.8+
    from unittest.mock import AsyncMock

    interaction.response.send_message = AsyncMock()

    # Call the callback directly since the attribute is a Command object
    await search_cog.search.callback(
        search_cog, interaction, query=None, character=None, unit=None, group=None, rarity=None
    )

    # Should send ephemeral message pointing to advanced_search
    interaction.response.send_message.assert_called_once()
    args, kwargs = interaction.response.send_message.call_args
    assert "Please provide at least one search filter" in args[0]
    assert kwargs.get("ephemeral") is True


@pytest.mark.asyncio
async def test_search_with_args(search_cog):
    interaction = MagicMock()
    from unittest.mock import AsyncMock

    interaction.response.defer = AsyncMock()
    interaction.followup.send = AsyncMock()
    search_cog.card_repo.search_cards.return_value = []  # Return empty list to avoid embed build error

    await search_cog.search.callback(
        search_cog, interaction, query="Test", character=None, unit=None, group=None, rarity=None
    )

    interaction.response.defer.assert_called_once()
    search_cog.card_repo.search_cards.assert_called_once()
    interaction.followup.send.assert_called_once()


@pytest.mark.asyncio
async def test_advanced_search_command(search_cog):
    interaction = MagicMock()
    from unittest.mock import AsyncMock

    interaction.response.send_message = AsyncMock()

    await search_cog.advanced_search.callback(search_cog, interaction)

    interaction.response.send_message.assert_called_once()
    args, kwargs = interaction.response.send_message.call_args
    assert "Launching Advanced Search Dashboard" in args[0]
    assert "view" in kwargs
    assert kwargs.get("ephemeral") is True
