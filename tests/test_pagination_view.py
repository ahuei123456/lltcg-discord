from unittest.mock import MagicMock

import discord
import pytest

from src.cogs.views.pagination_view import PaginationView


@pytest.fixture
def sample_results():
    return [{"name": f"Card {i}", "card_number": f"{i:03}", "rarity": "R"} for i in range(25)]


@pytest.mark.asyncio
async def test_pagination_view_init(sample_results):
    view = PaginationView(sample_results, "Title", "Filters", discord.Color.blue())
    assert view.total_pages == 3  # 25 items / 10 per page = 3 pages (10, 10, 5)
    assert view.current_page == 0
    assert view.btn_prev.disabled is True
    assert view.btn_next.disabled is False


@pytest.mark.asyncio
async def test_get_embed(sample_results):
    view = PaginationView(sample_results, "Title", "Filters", discord.Color.blue())
    embed = view.get_embed()

    assert embed.title == "Title"
    assert "Card 0" in embed.description
    assert "Card 9" in embed.description
    assert "Card 10" not in embed.description  # Page 1 ends at 9


@pytest.mark.asyncio
async def test_next_button(sample_results):
    view = PaginationView(sample_results, "Title", "Filters", discord.Color.blue())
    interaction = MagicMock()
    # Mock response
    from unittest.mock import AsyncMock

    interaction.response.edit_message = AsyncMock()

    # Click Next
    # The callback is bound to the view instance.
    # It seems for testing we can just call it with interaction?
    # Let's try passing just interaction.
    # If the signature is (self, interaction, button), keeping button is logically correct,
    # but maybe the way we access it via view.btn_next.callback binds it differently or it's a wrapper.
    # The error "takes 2 but 3 given" suggests (self, interaction) are the 2.
    # Let's try forcing it.
    await view.btn_next.callback(interaction)  # type: ignore

    assert view.current_page == 1
    interaction.response.edit_message.assert_called_once()

    # Verify embed for page 2
    embed = view.get_embed()
    assert "Card 10" in embed.description
    assert "Card 19" in embed.description


@pytest.mark.asyncio
async def test_back_callback(sample_results):
    cb = MagicMock()
    from unittest.mock import AsyncMock

    cb = AsyncMock()

    view = PaginationView(sample_results, "Title", "Filters", discord.Color.blue(), back_callback=cb)
    interaction = MagicMock()

    await view.btn_back.callback(interaction)  # type: ignore
    cb.assert_called_once_with(interaction)
