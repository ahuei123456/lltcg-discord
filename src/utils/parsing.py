def parse_range_string(val: str) -> tuple[int | None, int | None]:
    """
    Parses a range string into (min, max).
    Supported formats:
        "4"      -> (4, 4)      (Exact)
        "2-4"    -> (2, 4)      (Range)
        "4+"     -> (4, None)   (Min inclusive)
        ">=4"    -> (4, None)   (Min inclusive)
        ">4"     -> (5, None)   (Min exclusive -> Min + 1)
        "<=4"    -> (None, 4)   (Max inclusive)
        "<4"     -> (None, 3)   (Max exclusive -> Max - 1)

    Returns (None, None) if parsing fails.
    """
    if not val:
        return None, None

    val = val.strip().replace(" ", "")

    try:
        # Range "min-max"
        if "-" in val and not val.startswith("-"):
            # Basic check to avoid negative numbers confusion if we supported them.
            parts = val.split("-")
            if len(parts) == 2:
                return int(parts[0]), int(parts[1])

        # Min inclusive "X+"
        if val.endswith("+"):
            return int(val[:-1]), None

        # Comparisons
        if val.startswith(">="):
            return int(val[2:]), None
        if val.startswith(">"):
            return int(val[1:]) + 1, None
        if val.startswith("<="):
            return None, int(val[2:])
        if val.startswith("<"):
            return None, int(val[1:]) - 1

        # Exact value
        ival = int(val)
        return ival, ival

    except ValueError:
        return None, None
