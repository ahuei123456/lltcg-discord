from collections.abc import Callable

import discord
from discord.ui import Button, View

from src.db.card_repository import CardData


class PaginationView(View):
    def __init__(
        self,
        results: list[dict] | list[CardData],
        title: str,
        filters_desc: str,
        color: discord.Color,
        back_callback: Callable | None = None,
        items_per_page: int = 10,
    ):
        super().__init__(timeout=None)
        self.results = results
        self.title = title
        self.filters_desc = filters_desc
        self.color = color
        self.back_callback = back_callback
        self.items_per_page = items_per_page
        self.current_page = 0
        self.total_pages = (len(results) + items_per_page - 1) // items_per_page

        self._update_buttons()

    def _update_buttons(self):
        self.btn_first.disabled = self.current_page == 0
        self.btn_prev.disabled = self.current_page == 0
        self.btn_next.disabled = self.current_page == self.total_pages - 1
        self.btn_last.disabled = self.current_page == self.total_pages - 1

        self.btn_page_count.label = f"Page {self.current_page + 1}/{self.total_pages} ({len(self.results)})"

        if not self.back_callback:
            self.remove_item(self.btn_back)

    def get_embed(self) -> discord.Embed:
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        page_items = self.results[start:end]

        desc = self.filters_desc + "\n"
        for i, card in enumerate(page_items):
            # global index = start + i
            number = card.get("card_number", "???")
            name = card.get("name", "Unknown")
            rarity = card.get("rarity", "?")
            desc += f"`{number}` **{name}** ({rarity})\n"

        embed = discord.Embed(title=self.title, description=desc, color=self.color)
        embed.set_footer(text=f"Showing items {start + 1}-{min(end, len(self.results))} of {len(self.results)}")
        return embed

    async def update_view(self, interaction: discord.Interaction):
        self._update_buttons()
        embed = self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="<<", style=discord.ButtonStyle.secondary, row=0)
    async def btn_first(self, interaction: discord.Interaction, button: Button):
        self.current_page = 0
        await self.update_view(interaction)

    @discord.ui.button(label="<", style=discord.ButtonStyle.secondary, row=0)
    async def btn_prev(self, interaction: discord.Interaction, button: Button):
        if self.current_page > 0:
            self.current_page -= 1
        await self.update_view(interaction)

    @discord.ui.button(label="Page 1/1", style=discord.ButtonStyle.secondary, disabled=True, row=0)
    async def btn_page_count(self, interaction: discord.Interaction, button: Button):
        pass

    @discord.ui.button(label=">", style=discord.ButtonStyle.secondary, row=0)
    async def btn_next(self, interaction: discord.Interaction, button: Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
        await self.update_view(interaction)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.secondary, row=0)
    async def btn_last(self, interaction: discord.Interaction, button: Button):
        self.current_page = self.total_pages - 1
        await self.update_view(interaction)

    @discord.ui.button(label="Back to Search", style=discord.ButtonStyle.primary, row=1)
    async def btn_back(self, interaction: discord.Interaction, button: Button):
        if self.back_callback:
            await self.back_callback(interaction)
