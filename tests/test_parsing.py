import pytest

from src.utils.parsing import parse_range_string


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("4", (4, 4)),
        ("2-4", (2, 4)),
        ("4+", (4, None)),
        (">=4", (4, None)),
        (">4", (5, None)),
        ("<=4", (None, 4)),
        ("<4", (None, 3)),
        ("invalid", (None, None)),
        ("", (None, None)),
        (None, (None, None)),
    ],
)
def test_parse_range_string(input_str, expected):
    """Test parsing of range strings with various operators."""
    assert parse_range_string(input_str) == expected
