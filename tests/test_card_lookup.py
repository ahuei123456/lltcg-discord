from unittest.mock import MagicMock

import pytest

from src.cogs.card_lookup import CardLookup


@pytest.fixture
def card_lookup():
    bot = MagicMock()
    # Mock bot.emojis as an empty list so discord.utils.get works correctly in tests
    bot.emojis = []
    card_repo = MagicMock()
    # Mock config to avoid file I/O
    with MagicMock() as _:
        # We need to simulate the config.get_config() behavior
        return CardLookup(bot, card_repo)


def test_apply_ability_emojis_bracketed(card_lookup):
    text = "自分のが持つ[桃ブレード]、[赤ブレード]、[黄ブレード]、[緑ブレード]、[紫ブレード]、[青ブレード]になる。"
    result = card_lookup._apply_ability_emojis(text)
    assert ":blade_heart01:" in result
    assert ":blade_heart02:" in result
    assert ":blade_heart03:" in result
    assert ":blade_heart04:" in result
    assert ":blade_heart05:" in result
    assert ":blade_heart06:" in result


def test_apply_ability_emojis_boundaries(card_lookup):
    # Standalone matches
    text = "ハート ブレード E ALLブレード"
    result = card_lookup._apply_ability_emojis(text)
    assert ":icon_all:" in result
    assert ":icon_blade:" in result
    assert ":icon_energy:" in result
    assert ":sp_all:" in result


def test_apply_ability_emojis_no_boundary_fail(card_lookup):
    # Should NOT match because no spaces
    text = "エネルギーブレード"
    result = card_lookup._apply_ability_emojis(text)
    assert ":icon_energy:" not in result
    assert ":icon_blade:" not in result
    assert "エネルギーブレード" in result


def test_apply_ability_emojis_heart_codes(card_lookup):
    text = "heart01 heart02 heart03 heart04 heart05 heart06"
    result = card_lookup._apply_ability_emojis(text)
    assert ":heart01:" in result
    assert ":heart02:" in result
    assert ":heart03:" in result
    assert ":heart04:" in result
    assert ":heart05:" in result
    assert ":heart06:" in result


def test_apply_ability_emojis_complex_mix(card_lookup):
    # Note: Using spaces as per user requirement "surrounded by spaces"
    text = "起動 ターン1回 E E E ： ハート ハート ブレード ブレード を得る。"
    result = card_lookup._apply_ability_emojis(text)
    print(f"DEBUG RESULT: {result}")
    assert result.count(":icon_energy:") == 3
    assert result.count(":icon_all:") == 2
    assert result.count(":icon_blade:") == 2
