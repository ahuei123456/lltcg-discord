import logging

import discord
from discord import app_commands
from discord.ext import commands

from src.db.card_repository import CardRepository

_log = logging.getLogger(__name__)


class CardLookup(commands.Cog):
    def __init__(self, bot: commands.Bot, card_repo: CardRepository):
        self.bot = bot
        self.card_repo = card_repo

    async def series_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        matches = self.card_repo.search_series(current)
        return [app_commands.Choice(name=val, value=val) for val in matches]

    async def product_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        matches = self.card_repo.search_product(current)
        return [app_commands.Choice(name=val, value=val) for val in matches]

    async def rarity_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        matches = self.card_repo.search_rarity(current)
        return [app_commands.Choice(name=val, value=val) for val in matches]

    @app_commands.command(name="card", description="Look up a Love Live! OCG card")
    @app_commands.autocomplete(series=series_autocomplete, product=product_autocomplete, rarity=rarity_autocomplete)
    @app_commands.describe(
        series="Card Series (e.g. PL!N)",
        product="Product Code (e.g. bp4)",
        number="Card Number (e.g. 32)",
        rarity="Rarity (e.g. L+)",
    )
    async def card(self, interaction: discord.Interaction, series: str, product: str, number: int, rarity: str):
        await interaction.response.defer()

        # Pad number to 3 digits (e.g. 32 -> "032")
        number_str = f"{number:03d}"

        card_data = self.card_repo.get_card(series, product, number_str, rarity)

        if not card_data:
            # Try to help the user if they typed something close
            # But per spec, we require all 4 to match uniquely.
            await interaction.followup.send(
                f"Card not found: `{series}-{product}-{number_str}-{rarity}`.\nPlease check the ID components.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"{card_data['name']} ({card_data['rarity']})",
            description=f"**Set**: {card_data['set']}\n**Type**: {card_data['card_type']}",
            color=discord.Color.blue(),  # Default color, can be customized based on unit/group
        )

        if card_data.get("img_url"):
            # Ensure URL is properly encoded for Discord
            # We only want to quote the path part, but specific characters like ! need encoding
            from urllib.parse import quote

            url = card_data["img_url"]
            # Split protocol
            if "://" in url:
                proto, rest = url.split("://", 1)
                # Split path from domain - this is a simple heuristic
                # Assuming standard format https://domain.com/path/file.png
                parts = rest.split("/", 1)
                if len(parts) == 2:
                    domain, path = parts
                    # safe parameters: characters that should NOT be encoded.
                    # standard is '/', usually we want to encode everything else including '!'
                    # UPDATE: '!' seems to break some image servers if encoded, so we keep it safe.
                    encoded_path = quote(path, safe="/:?=&!")
                    url = f"{proto}://{domain}/{encoded_path}"

            embed.set_image(url=url)

        # Add Unit and Group info
        if card_data.get("unit"):
            embed.add_field(name="Unit", value=card_data["unit"], inline=True)

        if card_data.get("group"):
            # Group is a list of strings
            group_text = ", ".join(card_data["group"])
            embed.add_field(name="Group", value=group_text, inline=True)

        # Add basic fields
        if card_data.get("cost"):
            embed.add_field(name="Cost", value=card_data["cost"], inline=True)
        if card_data.get("score"):
            embed.add_field(name="Score", value=card_data["score"], inline=True)

        # Add hearts info if present
        hearts_info = []
        if card_data.get("hearts") and isinstance(card_data["hearts"], dict):
            formatted = ", ".join([f"{k}: {v}" for k, v in card_data["hearts"].items()])
            hearts_info.append(f"Hearts: {formatted}")

        if card_data.get("required_hearts") and isinstance(card_data["required_hearts"], dict):
            formatted = ", ".join([f"{k}: {v}" for k, v in card_data["required_hearts"].items()])
            hearts_info.append(f"Req. Hearts: {formatted}")

        if hearts_info:
            embed.add_field(name="Heart Stats", value="\n".join(hearts_info), inline=False)

        # Add Ability Text
        info_text = card_data.get("info_text")
        if info_text:
            text = "\n".join(info_text)
            # Discord field value limit is 1024 chars
            if len(text) > 1024:
                text = text[:1021] + "..."
            embed.add_field(name="Ability", value=text, inline=False)

        # Footer
        embed.set_footer(text=f"ID: {card_data['card_number']}")

        await interaction.followup.send(embed=embed)
