# Constants
COLOR_MAP = {
    "heart01": "Pink",
    "heart02": "Red",
    "heart03": "Yellow",
    "heart04": "Green",
    "heart05": "Blue",
    "heart06": "Purple",
    "heart0": "Gray",
}

# Standardized Blade Heart Map
BLADE_HEART_MAP = {
    "b_heart01": "Pink 🩷",
    "b_heart02": "Red ❤️",
    "b_heart03": "Yellow 💛",
    "b_heart04": "Green 💚",
    "b_heart05": "Blue 💙",
    "b_heart06": "Purple 💜",
    "ドロー": "Draw ✍️",
    "スコア": "Score 🎼",
    "ALL1": "All (Rainbow)",
}


class FilterState:
    def __init__(self):
        self.card_type: str | None = None  # Member, Live, etc.
        self.cost_min: int | None = None
        self.cost_max: int | None = None
        self.blades_min: int | None = None
        self.blades_max: int | None = None
        self.text_query: str | None = None
        self.card_number: str | None = None
        self.blade_hearts: list[str] = []
        self.hearts: dict[str, str] = {}  # {'heart01': '>=1'}

    def to_dict(self):
        d = {}
        if self.card_type:
            d["card_type"] = self.card_type
        if self.cost_min is not None:
            d["cost_min"] = self.cost_min
        if self.cost_max is not None:
            d["cost_max"] = self.cost_max
        if self.blades_min is not None:
            d["blades_min"] = self.blades_min
        if self.blades_max is not None:
            d["blades_max"] = self.blades_max
        if self.text_query:
            d["text_query"] = self.text_query
        if self.card_number:
            d["card_number"] = self.card_number
        if self.blade_hearts:
            d["blade_hearts"] = self.blade_hearts
        if self.hearts:
            d["hearts"] = self.hearts
        return d

    def describe_filters(self) -> str:
        parts = []
        if self.card_type:
            parts.append(f"Type: {self.card_type}")
        if self.cost_min or self.cost_max:
            parts.append(f"Cost: {self.cost_min or 0}-{self.cost_max or 'Inf'}")
        if self.blades_min or self.blades_max:
            parts.append(f"Blades: {self.blades_min or 0}-{self.blades_max or 'Inf'}")
        if self.text_query:
            parts.append(f"Text: '{self.text_query}'")
        if self.card_number:
            parts.append(f"Num: '{self.card_number}'")
        if self.blade_hearts:
            bh_labels = [BLADE_HEART_MAP.get(k, k) for k in self.blade_hearts]
            parts.append(f"Blade Hearts: {', '.join(bh_labels)}")
        if self.hearts:
            h_desc = ", ".join([f"{COLOR_MAP.get(k, k)}:{v}" for k, v in self.hearts.items()])
            parts.append(f"Hearts: {h_desc}")

        return "\n".join(parts) if parts else "No filters set."
