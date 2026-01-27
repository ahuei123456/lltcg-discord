from collections.abc import Callable

import discord
from discord.ui import Button, Modal, Select, TextInput, View

from .state import FilterState

# Import HeartConfigView inside the method to avoid circular import if needed
# Or just import here locally if clean.


class TextFilterModal(Modal, title="Text Filters"):
    name: TextInput = TextInput(label="Name / Text Query", required=False, max_length=100)
    number: TextInput = TextInput(label="Card Number (Partial)", required=False, max_length=20)

    def __init__(self, current_text: str | None, current_num: str | None, callback: Callable):
        super().__init__()
        if current_text:
            self.name.default = current_text
        if current_num:
            self.number.default = current_num
        self.callback = callback

    async def on_submit(self, interaction: discord.Interaction):
        await self.callback(interaction, self.name.value, self.number.value)


class RangeFilterModal(Modal, title="Numeric Ranges"):
    cost_range: TextInput = TextInput(label="Cost Range (e.g. 1-3)", required=False, placeholder="Min-Max")
    blades_range: TextInput = TextInput(label="Blades Range (e.g. 2-2)", required=False, placeholder="Min-Max")

    def __init__(self, callback: Callable):
        super().__init__()
        self.callback = callback

    def parse_range(self, val: str) -> tuple[int | None, int | None]:
        if not val or "-" not in val:
            return None, None
        try:
            parts = val.split("-")
            min_v = int(parts[0]) if parts[0].strip() else None
            max_v = int(parts[1]) if parts[1].strip() else None
            return min_v, max_v
        except Exception:
            return None, None

    async def on_submit(self, interaction: discord.Interaction):
        c_min, c_max = self.parse_range(self.cost_range.value)
        b_min, b_max = self.parse_range(self.blades_range.value)
        await self.callback(interaction, c_min, c_max, b_min, b_max)


class StartSearchView(View):
    def __init__(self, callback: Callable, initial_state: FilterState | None = None):
        super().__init__(timeout=None)
        self.callback = callback
        self.filters = initial_state if initial_state else FilterState()
        self._update_components()

    def _update_components(self):
        # We might want to reflect self.filters in the UI (e.g. initial select values)
        # However, for Select Menus, setting `default` on options usually requires rebuilding the options list.
        # For simplicity MVP: we validly hold the state, but might not visually reflect it on the
        # standard buttons/dropdown unless we add logic here to pre-select items in `select_type` etc.
        # Let's try to update placeholders at least or something?
        # Actually, for Selects, we can set `default=True` on options matching the state.
        pass

    @discord.ui.select(
        placeholder="Filter by Card Type...",
        options=[
            discord.SelectOption(label="All Types", value="ALL"),
            discord.SelectOption(label="Member", value="メンバー"),
            discord.SelectOption(label="Live", value="ライブ"),
        ],
        row=0,
    )
    async def select_type(self, interaction: discord.Interaction, select: Select):
        val = select.values[0]
        self.filters.card_type = val if val != "ALL" else None
        await self.refresh_embed(interaction)

    @discord.ui.button(label="Edit Text/Number", style=discord.ButtonStyle.secondary, row=1)
    async def btn_text(self, interaction: discord.Interaction, button: Button):
        async def cb(itr, text, num):
            self.filters.text_query = text if text else None
            self.filters.card_number = num if num else None
            await self.refresh_embed(itr)

        await interaction.response.send_modal(TextFilterModal(self.filters.text_query, self.filters.card_number, cb))

    @discord.ui.button(label="Set Cost/Blades", style=discord.ButtonStyle.secondary, row=1)
    async def btn_ranges(self, interaction: discord.Interaction, button: Button):
        async def cb(itr, c_min, c_max, b_min, b_max):
            self.filters.cost_min, self.filters.cost_max = c_min, c_max
            self.filters.blades_min, self.filters.blades_max = b_min, b_max
            await self.refresh_embed(itr)

        await interaction.response.send_modal(RangeFilterModal(cb))

    @discord.ui.select(
        placeholder="Blade Hearts (Match ANY)...",
        min_values=0,
        max_values=9,
        options=[
            discord.SelectOption(label="Pink 🩷", value="b_heart01"),
            discord.SelectOption(label="Red ❤️", value="b_heart02"),
            discord.SelectOption(label="Yellow 💛", value="b_heart03"),
            discord.SelectOption(label="Green 💚", value="b_heart04"),
            discord.SelectOption(label="Blue 💙", value="b_heart05"),
            discord.SelectOption(label="Purple 💜", value="b_heart06"),
            discord.SelectOption(label="Draw ✍️", value="ドロー"),
            discord.SelectOption(label="Score 🎼", value="スコア"),
            discord.SelectOption(label="All (Rainbow)", value="ALL1"),
        ],
        row=2,
    )
    async def select_blade_hearts(self, interaction: discord.Interaction, select: Select):
        self.filters.blade_hearts = select.values
        await self.refresh_embed(interaction)

    @discord.ui.button(label="Configure Hearts", style=discord.ButtonStyle.primary, row=3)
    async def btn_hearts(self, interaction: discord.Interaction, button: Button):
        from .heart_config_view import HeartConfigView

        async def back_cb(itr):
            await self.refresh_embed(itr)

        view = HeartConfigView(self.filters, back_cb)
        await view.refresh_display(interaction)

    @discord.ui.button(label="Search", style=discord.ButtonStyle.success, row=4)
    async def btn_search(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="Searching...", view=None, embed=None)
        await self.callback(interaction, self.filters)

    @discord.ui.button(label="Clear All", style=discord.ButtonStyle.danger, row=4)
    async def btn_clear(self, interaction: discord.Interaction, button: Button):
        self.filters = FilterState()
        await self.refresh_embed(interaction)

    async def refresh_embed(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Advanced Search Filters", color=discord.Color.blue())
        desc = self.filters.describe_filters()
        embed.description = f"```\n{desc}\n```"
        try:
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception:
            await interaction.edit_original_response(embed=embed, view=self)
