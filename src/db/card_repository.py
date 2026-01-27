import json
import logging
from dataclasses import dataclass
from typing import Optional, TypedDict

_log = logging.getLogger(__name__)


class CardData(TypedDict):
    card_number: str
    img_url: str
    name: str
    set: str
    card_type: str
    group: list[str]
    unit: str | None
    rarity: str
    # Optional fields depending on card type
    score: str | None
    cost: str | None
    blades: str | None
    hearts: dict[str, str] | None
    required_hearts: dict[str, str] | None
    blade_hearts: dict[str, str] | None
    special_hearts: str | None
    info_text: list[str] | None


@dataclass
class CardID:
    series: str
    product: str
    number: str
    rarity: str

    @classmethod
    def parse(cls, card_number: str) -> Optional["CardID"]:
        # Normalize: convert fullwidth + to ascii +
        normalized_number = card_number.replace("＋", "+")

        parts = normalized_number.split("-")
        if len(parts) != 4:
            return None

        return cls(series=parts[0], product=parts[1], number=parts[2], rarity=parts[3])


class CardRepository:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self._cards: list[CardData] = []

        # Indices for efficient lookup and autocomplete (stored as sorted lists)
        self._series_index: list[str] = []
        self._product_index: list[str] = []
        self._number_index: list[str] = []
        self._rarity_index: list[str] = []

        # Main lookup map: "series-product-number-rarity" (normalized) -> CardData
        self._id_map: dict[str, CardData] = {}

    def load_data(self) -> None:
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            # The JSON structure has a root key, typically "PBN" or similar lists.
            # Based on the user's file content, it looks like {"PBN": [...]}.
            # We should flatten all lists found in the root object.

            all_cards = []
            for key, card_list in raw_data.items():
                if isinstance(card_list, list):
                    all_cards.extend(card_list)

            self._cards = all_cards
            self._build_indices()
            _log.info(f"Loaded {len(self._cards)} cards from {self.data_path}")

        except FileNotFoundError:
            _log.error(f"Card data file not found at {self.data_path}")
            raise
        except json.JSONDecodeError:
            _log.error(f"Failed to decode JSON from {self.data_path}")
            raise

    def _build_indices(self) -> None:
        # Temporary sets to collect unique values
        series_set: set[str] = set()
        product_set: set[str] = set()
        number_set: set[str] = set()
        rarity_set: set[str] = set()

        self._id_map.clear()

        for card in self._cards:
            card_number = card.get("card_number", "")
            if not card_number:
                continue

            parsed_id = CardID.parse(card_number)
            if not parsed_id:
                _log.warning(f"Skipping malformed card number: {card_number}")
                continue

            # Store unique parts for autocomplete
            series_set.add(parsed_id.series)
            product_set.add(parsed_id.product)
            number_set.add(parsed_id.number)
            rarity_set.add(parsed_id.rarity)

            # Map normalized ID string to card data
            # Reconstruct ID with ASCII + for consistent lookup key
            normalized_key = f"{parsed_id.series}-{parsed_id.product}-{parsed_id.number}-{parsed_id.rarity}"
            self._id_map[normalized_key] = card

        # Convert sets to sorted lists for efficient autocomplete
        self._series_index = sorted(list(series_set))
        self._product_index = sorted(list(product_set))
        self._number_index = sorted(list(number_set))
        self._rarity_index = sorted(list(rarity_set))

    def get_card(self, series: str, product: str, number: str, rarity: str) -> CardData | None:
        """
        Retrieves a card by its components.
        Inputs are expected to be potentially user-typed (checking normalization).
        """
        # Ensure input rarity is normalized
        rarity = rarity.replace("＋", "+")
        key = f"{series}-{product}-{number}-{rarity}"
        return self._id_map.get(key)

    def search_series(self, query: str) -> list[str]:
        return self._search_index(self._series_index, query)

    def search_product(self, query: str) -> list[str]:
        return self._search_index(self._product_index, query)

    def search_number(self, query: str) -> list[str]:
        return self._search_index(self._number_index, query)

    def search_rarity(self, query: str) -> list[str]:
        return self._search_index(self._rarity_index, query)

    def _search_index(self, index: list[str], query: str) -> list[str]:
        """Case-insensitive partial match for autocomplete using pre-sorted list."""
        query = query.lower()
        # Since 'index' is already sorted, we don't need to sort again.
        # We just filter the list.
        matches = [val for val in index if query in val.lower()]
        return matches[:25]  # Discord limit is 25 choices

    def search_cards(
        self,
        query: str | None = None,
        # Legacy arguments for backward compatibility (mapped to filters internally if needed)
        character: str | None = None,
        unit: str | None = None,
        group: str | None = None,
        rarity: str | None = None,
        # New advanced filters
        filters: dict | None = None,
        limit: int = 25,
    ) -> list[CardData]:
        """
        Searches for cards based on various filters.
        Supports both legacy individual arguments and a comprehensive `filters` dict.

        filters dict keys:
            - cost_min, cost_max: int
            - blades_min, blades_max: int
            - text_query: str (partial match in name, info_text)
            - card_number: str (partial match)
            - card_type: str (Member, Live, etc.)
            - hearts: dict { color_key: operator_val } (e.g. {'heart01': '>=2'})
            - blade_hearts: list[str] (OR logic: requires at least one)
        """
        # Normalize inputs
        filters = filters or {}

        # Merge legacy args into filters if present (priority to explicit filters)
        if character:
            filters.setdefault("character", character)
        if unit:
            filters.setdefault("unit", unit)
        if group:
            filters.setdefault("group", group)
        if rarity:
            filters.setdefault("rarity", rarity)
        if query:
            filters.setdefault("query", query)  # Maps to legacy "query" logic (Name search)

        # Extraction for cleaner loop
        f_char = filters.get("character")
        f_unit = filters.get("unit")
        f_group = filters.get("group")
        f_rarity = filters.get("rarity")
        f_query = filters.get("query")  # Legacy Name-only search

        f_text_query = filters.get("text_query")  # Advanced Text search (Name + Info)

        _log.info(f"Searching cards with filters: {filters}")
        f_card_number = filters.get("card_number")
        f_card_type = filters.get("card_type")

        f_cost_min = filters.get("cost_min")
        f_cost_max = filters.get("cost_max")
        f_blades_min = filters.get("blades_min")
        f_blades_max = filters.get("blades_max")

        f_hearts = filters.get("hearts")  # Dict { 'heart01': '>=1' }
        f_blade_hearts = filters.get("blade_hearts")  # List ['b_heart01', ...]

        # Normalize rarity
        if f_rarity:
            f_rarity = f_rarity.replace("＋", "+")

        results = []
        for card in self._cards:
            # --- 1. Basic String Filters ---
            if f_rarity and card.get("rarity") != f_rarity:
                continue

            # Character (Name segment) - Normalized
            if f_char:
                norm_char = f_char.replace(" ", "")
                norm_card_name = card.get("name", "").replace(" ", "")
                if norm_char not in norm_card_name:
                    continue

            # Unit (Precise)
            if f_unit and card.get("unit") != f_unit:
                continue

            # Group (List containment)
            if f_group and f_group not in card.get("group", []):
                continue

            # Legacy Query (Name only)
            if f_query and f_query.lower() not in card.get("name", "").lower():
                continue

            # --- 2. Advanced Filters ---

            # Card Number (Partial)
            if f_card_number and f_card_number.lower() not in card.get("card_number", "").lower():
                continue

            # Card Type (Exact)
            if f_card_type and f_card_type != card.get("card_type"):
                continue

            # Text Query (Name OR Info Text)
            if f_text_query:
                q_lower = f_text_query.lower()
                in_name = q_lower in card.get("name", "").lower()
                in_info = False
                info_text = card.get("info_text")
                if info_text:
                    # info_text is list of strings
                    in_info = any(q_lower in line.lower() for line in info_text)

                if not (in_name or in_info):
                    continue

            # Numeric Ranges (Helper)
            def check_range(val_str: str | None, min_v: int | None, max_v: int | None) -> bool:
                if not val_str:
                    return False
                try:
                    val = int(val_str)
                    if min_v is not None and val < min_v:
                        return False
                    return not (max_v is not None and val > max_v)
                except ValueError:
                    return False  # Treat non-int as mismatch

            if (f_cost_min is not None or f_cost_max is not None) and not check_range(
                card.get("cost"), f_cost_min, f_cost_max
            ):
                continue

            if (f_blades_min is not None or f_blades_max is not None) and not check_range(
                card.get("blades"), f_blades_min, f_blades_max
            ):
                continue

            # Hearts Logic
            # "hearts" field in DB for Members (Base Hearts). "required_hearts" for Lives.
            # "hearts" filter keys: {'heart01': 2} means "At least 2 Pink".
            # We check BOTH `hearts` and `required_hearts` fields on the card.
            if f_hearts:
                card_hearts = card.get("hearts") or {}
                card_req_hearts = card.get("required_hearts") or {}
                # Merge for checking? Or check availability?
                # Usually filter means "Show cards that HAVE this heart config".
                # For member: "hearts" = cost validation?
                # DB structure: "hearts": {"heart01": "2"}

                match_failed = False
                for color_key, req_val_expr in f_hearts.items():
                    # req_val_expr e.g. ">=1" (from UI?) or just int 1?
                    # Let's assume input is simple int for "At least X"
                    # User UI: Click "2" -> means "Cards with 2 or more of this color"

                    req_min = int(req_val_expr)  # Assuming simple int value passed

                    # Check both fields
                    val_c = int(card_hearts.get(color_key, "0"))
                    val_r = int(card_req_hearts.get(color_key, "0"))
                    total_card_val = val_c + val_r

                    if total_card_val < req_min:
                        match_failed = True
                        break
                if match_failed:
                    continue

            # Blade Hearts Logic (OR Logic)
            # f_blade_hearts = ['b_heart01', 'ALL1']
            if f_blade_hearts:
                card_b_hearts = card.get("blade_hearts") or {}
                # Check if card has ANY of the requested keys
                # card_b_hearts keys: "b_heart01", "ALL1"

                has_any = False
                for req_k in f_blade_hearts:
                    if req_k in card_b_hearts:
                        has_any = True
                        break

                if not has_any:
                    continue

            results.append(card)
            if len(results) >= limit:
                break

        _log.info(
            f"Standard Search Results: Found {len(results)} cards. IDs: {[c.get('card_number') for c in results[:20]]}"
        )
        return results[:limit]
