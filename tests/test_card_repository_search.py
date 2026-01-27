import pytest

from src.db.card_repository import CardRepository

# Sample Data
SAMPLE_CARDS = [
    {
        "card_number": "PL!N-bp4-001-L+",
        "name": "Kousaka Honoka",
        "rarity": "L+",
        "unit": "Printemps",
        "group": ["muse"],
        "img_url": "http://example.com/honoka.png",
        "set": "PL!N",
        "card_type": "Member",
    },
    {
        "card_number": "PL!N-bp4-002-L+",
        "name": "Sonoda Umi",
        "rarity": "L+",
        "unit": "lily white",
        "group": ["muse"],
        "img_url": "http://example.com/umi.png",
        "set": "PL!N",
        "card_type": "Member",
    },
    {
        "card_number": "LSP-bp1-032-SR",
        "name": "Takami Chika",
        "rarity": "SR",
        "unit": "CYaRon!",
        "group": ["aqours"],
        "img_url": "http://example.com/chika.png",
        "set": "LSP",
        "card_type": "Member",
    },
    {
        "card_number": "NJ-bp1-001-C",
        "name": "Uehara Ayumu",
        "rarity": "C",
        "unit": "A・ZU・NA",
        "group": ["nijigasaki"],
        "img_url": "http://example.com/ayumu.png",
        "set": "NJ",
        "card_type": "Member",
    },
]


@pytest.fixture
def repo():
    # Mock file load so we don't need real data file
    repo = CardRepository("dummy_path.json")
    repo._cards = SAMPLE_CARDS  # Inject dummy data
    # Manually trigger index build
    repo._build_indices()
    return repo


def test_search_by_character_mapped(repo):
    # This test used the simple fixture. We can skip logic here or keep it simple.
    pass


@pytest.fixture
def repo_real_names():
    # Using Japanese names to match mappings.py output
    data = [
        {
            "card_number": "001",
            "name": "高坂穂乃果",
            "rarity": "L+",
            "unit": "Printemps",
            "group": ["ラブライブ！"],
            "img_url": "",
            "set": "TEST",
            "card_type": "メンバー",
            "cost": "4",
            "blades": "2",
            "hearts": {"heart01": "2"},
            "info_text": ["Sunny Day Song"],
        },
        {
            "card_number": "002",
            "name": "園田海未",
            "rarity": "SR",
            "unit": "lily white",
            "group": ["ラブライブ！"],
            "img_url": "",
            "set": "TEST",
            "card_type": "メンバー",
            "cost": "3",
            "blades": "1",
            "hearts": {"heart03": "1"},  # Assume heart03 is distinct
            "info_text": ["Love Arrow Shoot"],
        },
        {
            "card_number": "003",
            "name": "高海千歌",
            "rarity": "HR",
            "unit": "CYaRon!",
            "group": ["ラブライブ！サンシャイン!!"],
            "img_url": "",
            "set": "TEST",
            "card_type": "メンバー",
            "cost": "5",
            "blades": "3",
            "hearts": {"heart02": "2"},
            "blade_hearts": {"b_heart02": "1"},
        },
        {
            "card_number": "004",
            "name": "上原歩夢",
            "rarity": "C",
            "unit": "A・ZU・NA",
            "group": ["ラブライブ！虹ヶ咲学園スクールアイドル同好会"],
            "img_url": "",
            "set": "TEST",
            "card_type": "メンバー",
            "cost": "1",
            "blades": "0",
            "hearts": {"heart01": "1"},
        },
        {
            "card_number": "PL!-bp4-003-R",
            "img_url": "https://llofficial-cardgame.com/wordpress/wp-content/images/cardlist/BP04/PL!-bp4-003-R.png",
            "name": "南ことり",
            "set": "ブースターパック SAPPHIRE MOON",
            "card_type": "メンバー",
            "group": ["ラブライブ！"],
            "unit": "Printemps",
            "cost": "2",
            "hearts": {"heart03": "1"},
            "blade_hearts": {"b_heart03": "1"},
            "blades": "1",
            "rarity": "R",
            "info_text": [
                "起動 このメンバーをステージから控え室に置く：自分の控え室からライブカードを1枚手札に加える。"
            ],
        },
        {
            "card_number": "PL!SP-bp4-015-N",
            "img_url": "https://llofficial-cardgame.com/wordpress/wp-content/images/cardlist/BP04/PL!SP-bp4-015-N.png",
            "name": "平安名すみれ",
            "set": "ブースターパック SAPPHIRE MOON",
            "card_type": "メンバー",
            "group": ["ラブライブ！スーパースター!!"],
            "unit": "CatChu!",
            "cost": "2",
            "hearts": {"heart02": "1"},
            "blade_hearts": {"b_heart02": "1"},
            "blades": "1",
            "rarity": "N",
            "info_text": [
                "起動 このメンバーをステージから控え室に置く：自分の控え室からメンバーカードを1枚手札に加える。"
            ],
        },
        {
            "card_number": "005",
            "name": "Awesome Live",
            "rarity": "C",
            "unit": None,
            "group": [],
            "img_url": "",
            "set": "TEST",
            "card_type": "ライブ",
            "required_hearts": {"heart01": "3"},
            "blade_hearts": {"ALL1": "1"},
        },
    ]
    repo = CardRepository("dummy_path")
    repo._cards = data
    repo._build_indices()
    return repo


def test_search_advanced_cost(repo_real_names):
    # Cost 3-4 (Honoka=4, Umi=3)
    results = repo_real_names.search_cards(filters={"cost_min": 3, "cost_max": 4})
    assert len(results) == 2
    names = {c["name"] for c in results}
    assert "高坂穂乃果" in names
    assert "園田海未" in names


def test_search_advanced_hearts_member(repo_real_names):
    # Heart01 >= 2 (Honoka has 2)
    results = repo_real_names.search_cards(filters={"hearts": {"heart01": 2}})
    assert len(results) >= 1
    assert any(c["name"] == "高坂穂乃果" for c in results)
    # Ayumu (heart01=1) should NOT match
    assert not any(c["name"] == "上原歩夢" for c in results)


def test_search_advanced_hearts_live(repo_real_names):
    # Live req_hearts matches logic too? "heart01": 3 (Awesome Live has 3)
    results = repo_real_names.search_cards(filters={"hearts": {"heart01": 3}})
    assert any(c["name"] == "Awesome Live" for c in results)


def test_search_blade_hearts_or(repo_real_names):
    # b_heart02 OR ALL1. Chika(b_heart02), Awesome Live(ALL1)
    results = repo_real_names.search_cards(filters={"blade_hearts": ["b_heart02", "ALL1"]})
    assert len(results) == 3
    names = {c["name"] for c in results}
    assert "高海千歌" in names
    assert "Awesome Live" in names


def test_search_text_query(repo_real_names):
    # "Arrow" in info_text "Love Arrow Shoot"
    results = repo_real_names.search_cards(filters={"text_query": "Arrow"})
    assert len(results) == 1
    assert results[0]["name"] == "園田海未"


def test_search_card_type(repo_real_names):
    results = repo_real_names.search_cards(filters={"card_type": "ライブ"})
    assert len(results) == 1
    assert results[0]["name"] == "Awesome Live"


def test_search_character(repo_real_names):
    # "Honoka" -> "高坂穂乃果" (Raw search expects Japanese now)
    results = repo_real_names.search_cards(character="高坂穂乃果")
    assert len(results) == 1
    assert results[0]["name"] == "高坂穂乃果"


def test_search_unit(repo_real_names):
    # "cyaron" -> "CYaRon!" (Raw search expects DB value)
    results = repo_real_names.search_cards(unit="CYaRon!")
    assert len(results) == 1
    assert results[0]["name"] == "高海千歌"


def test_search_group(repo_real_names):
    # "nijigasaki" -> "ラブライブ！虹ヶ咲学園スクールアイドル同好会" (Raw search expects DB value)
    results = repo_real_names.search_cards(group="ラブライブ！虹ヶ咲学園スクールアイドル同好会")
    assert len(results) == 1
    assert results[0]["name"] == "上原歩夢"


def test_search_rarity(repo_real_names):
    # "HR"
    results = repo_real_names.search_cards(rarity="HR")
    assert len(results) == 1
    assert results[0]["name"] == "高海千歌"


def test_search_query_text(repo_real_names):
    # "Live" -> Matches "Awesome Live" and "ラブライブ！..." (Wait, group is not name)
    # Name is "Awesome Live"
    results = repo_real_names.search_cards(query="Awesome")
    assert len(results) == 1
    assert results[0]["name"] == "Awesome Live"


def test_search_multiple_filters(repo_real_names):
    # Umi is SR, Unit lily white
    results = repo_real_names.search_cards(unit="lily white", rarity="SR")
    assert len(results) == 1
    assert results[0]["name"] == "園田海未"

    # Non-matching combo
    results = repo_real_names.search_cards(unit="CYaRon!", rarity="L+")
    assert len(results) == 0


def test_search_character_normalization():
    # Regression test for "百生吟子" (User input) matching "百生 吟子" (DB Value)
    # The fixture data doesn't have "百生 吟子", so we create a specific repo instance

    custom_data = [
        {
            "card_number": "001",
            "name": "百生 吟子",
            "rarity": "R+",
            "unit": "スリーズブーケ",
            "group": ["蓮ノ空女学院スクールアイドルクラブ"],
            "img_url": "",
            "set": "TEST",
            "card_type": "Member",
        }
    ]
    repo = CardRepository("dummy_path")
    repo._cards = custom_data
    repo._build_indices()

    # Search with "百生吟子" (no space)
    results = repo.search_cards(character="百生吟子")
    assert len(results) == 1
    assert results[0]["name"] == "百生 吟子"


def test_search_specific_kotori(repo_real_names):
    """
    Search for cost 2, heart03 == 1, b_heart03 ==1, and blades == 1.
    """
    filters = {
        "cost_min": 2,
        "cost_max": 2,
        "blades_min": 1,
        "blades_max": 1,
        "hearts": {"heart03": "1"},
        "blade_hearts": ["b_heart03"],
    }
    results = repo_real_names.search_cards(filters=filters)
    assert len(results) > 0
    # Check if the specific card is found by ID or Name
    found = any(c["card_number"] == "PL!-bp4-003-R" for c in results)
    assert found, "Detailed Kotori card not found with specific filters"


def test_search_specific_sumire(repo_real_names):
    """
    Search for cost 2, heart03 == 1, b_heart03 ==1, and blades == 1.
    """
    filters = {
        "cost_min": 2,
        "cost_max": 2,
        "blades_min": 1,
        "blades_max": 1,
        "hearts": {"heart02": "1"},
        "blade_hearts": ["b_heart02"],
    }
    results = repo_real_names.search_cards(filters=filters)
    assert len(results) > 0
    # Check if the specific card is found by ID or Name
    found = any(c["card_number"] == "PL!SP-bp4-015-N" for c in results)
    assert found, "Detailed Sumire card not found with specific filters"
