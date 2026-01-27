from collections.abc import Callable

import discord
from discord.ui import Button, Select, View

from .state import COLOR_MAP, FilterState


class HeartConfigView(View):
    def __init__(self, filters: FilterState, back_callback: Callable):
        super().__init__(timeout=300)
        self.filters = filters
        self.back_callback = back_callback
        self.selected_color = "heart01"  # Default to first

    async def refresh_display(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Configure Heart Requirements", color=discord.Color.magenta())
        # Show current state
        desc = self.filters.describe_filters()
        embed.description = (
            f"Current Settings:\n```\n{desc}\n```\n"
            "**Instructions:** Select a Color below, then click a Number to set minimum requirement for that color."
        )

        try:
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception:
            await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.select(
        placeholder="Select Color to Configure...",
        options=[
            discord.SelectOption(label="Pink", value="heart01"),
            discord.SelectOption(label="Red", value="heart02"),
            discord.SelectOption(label="Yellow", value="heart03"),
            discord.SelectOption(label="Green", value="heart04"),
            discord.SelectOption(label="Blue", value="heart05"),
            discord.SelectOption(label="Purple", value="heart06"),
            discord.SelectOption(label="Gray", value="heart0"),
        ],
        row=0,
    )
    async def select_color(self, interaction: discord.Interaction, select: Select):
        self.selected_color = select.values[0]
        # Just acknowledge, no visible change unless we show "Selected: Pink" in embed
        if interaction.message and interaction.message.embeds:
            embed = interaction.message.embeds[0]
            # Maybe append to footer?
            embed.set_footer(text=f"Selected Color: {COLOR_MAP.get(self.selected_color, self.selected_color)}")
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    async def _update_heart(self, interaction: discord.Interaction, val: str):
        self.filters.hearts[self.selected_color] = val
        await self.refresh_display(interaction)

    @discord.ui.button(label="1", style=discord.ButtonStyle.secondary, row=1)
    async def btn_1(self, interaction: discord.Interaction, button: Button):
        await self._update_heart(interaction, "1")

    @discord.ui.button(label="2", style=discord.ButtonStyle.secondary, row=1)
    async def btn_2(self, interaction: discord.Interaction, button: Button):
        await self._update_heart(interaction, "2")

    @discord.ui.button(label="3", style=discord.ButtonStyle.secondary, row=1)
    async def btn_3(self, interaction: discord.Interaction, button: Button):
        await self._update_heart(interaction, "3")

    @discord.ui.button(label="4+", style=discord.ButtonStyle.secondary, row=1)
    async def btn_4(self, interaction: discord.Interaction, button: Button):
        await self._update_heart(interaction, "4")

    @discord.ui.button(label="Clear This Color", style=discord.ButtonStyle.danger, row=1)
    async def btn_clear_color(self, interaction: discord.Interaction, button: Button):
        if self.selected_color in self.filters.hearts:
            del self.filters.hearts[self.selected_color]
        await self.refresh_display(interaction)

    @discord.ui.button(label="<< Back to Dashboard", style=discord.ButtonStyle.primary, row=2)
    async def btn_back(self, interaction: discord.Interaction, button: Button):
        await self.back_callback(interaction)
