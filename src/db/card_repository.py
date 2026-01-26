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
