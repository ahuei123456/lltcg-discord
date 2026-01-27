from src.cogs.views.state import FilterState


def test_filter_state_defaults():
    fs = FilterState()
    assert fs.to_dict() == {}
    assert "No filters set" in fs.describe_filters()


def test_filter_state_population():
    fs = FilterState()
    fs.card_type = "Member"
    fs.cost_min = 1
    fs.cost_max = 5
    fs.text_query = "Honoka"

    d = fs.to_dict()
    assert d["card_type"] == "Member"
    assert d["cost_min"] == 1
    assert d["cost_max"] == 5
    assert d["text_query"] == "Honoka"

    desc = fs.describe_filters()
    assert "Type: Member" in desc
    assert "Cost: 1-5" in desc
    assert "Text: 'Honoka'" in desc


def test_filter_state_hearts():
    fs = FilterState()
    fs.hearts = {"heart01": "2"}
    fs.blade_hearts = ["b_heart01", "ALL1"]

    d = fs.to_dict()
    assert d["hearts"] == {"heart01": "2"}
    assert d["blade_hearts"] == ["b_heart01", "ALL1"]

    desc = fs.describe_filters()
    assert "Pink:2" in desc
    assert "Pink 🩷" in desc
    assert "All (Rainbow)" in desc
