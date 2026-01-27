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

        # key -> emoji_name mapping based on user request
        # Used for heart stats and ability text replacement
        emoji_map = {
            "heart01": "heart01",  # Pink
            "heart02": "heart02",  # Red
            "heart03": "heart03",  # Yellow
            "heart04": "heart04",  # Green
            "heart05": "heart05",  # Blue
            "heart06": "heart06",  # Purple
            "heart0": "heart00",  # Grey
            "ALL1": "sp_all",  # All (Blade Heart generic)
            # Blade Hearts specific mappings (b_heart0X)
            "b_heart01": "blade_heart01",
            "b_heart02": "blade_heart02",
            "b_heart03": "blade_heart03",
            "b_heart04": "blade_heart04",
            "b_heart05": "blade_heart05",
            "b_heart06": "blade_heart06",
            "ALL": "sp_all",  # Possible variation
            # Special hearts
            "ドロー": "sp_draw",
            "スコア": "sp_score",
        }

        # Helper to format hearts with emojis
        def format_hearts(hearts_data: dict[str, str]) -> str:
            parts = []
            for key, amount in hearts_data.items():
                emoji_name = emoji_map.get(key, key)
                # Try to find the emoji by name in the bot's cache
                emoji = discord.utils.get(self.bot.emojis, name=emoji_name)

                display_emoji = str(emoji) if emoji else f":{emoji_name}:"
                parts.append(f"{display_emoji} {amount}")

            return "   ".join(parts)

        # Re-ordering to match the screenshot: Required First, then Blade Heart

        # Required Hearts
        if card_data.get("required_hearts") and isinstance(card_data["required_hearts"], dict):
            text = format_hearts(card_data["required_hearts"])
            embed.add_field(name="Required Hearts", value=text, inline=False)

        # Merge Blade Hearts (dict) and Special Hearts (string)
        blade_hearts_parts = []

        # 1. Process Blade Hearts dict
        if card_data.get("blade_hearts") and isinstance(card_data["blade_hearts"], dict):
            blade_hearts_parts.append(format_hearts(card_data["blade_hearts"]))

        # 2. Process Special Hearts string
        special_hearts_str = card_data.get("special_hearts")
        if special_hearts_str:
            # Check if we have an emoji mapping
            emoji_name = emoji_map.get(special_hearts_str)
            if emoji_name:
                emoji = discord.utils.get(self.bot.emojis, name=emoji_name)
                display_val = str(emoji) if emoji else f":{emoji_name}:"
                blade_hearts_parts.append(display_val)
            else:
                # Fallback to just text if no mapping
                blade_hearts_parts.append(special_hearts_str)

        # Combine and display if any exist
        if blade_hearts_parts:
            combined_text = "   ".join(blade_hearts_parts)
            embed.add_field(name="Blade Heart", value=combined_text, inline=False)

        # Just in case 'hearts' is used for something else or as a fallback
        if card_data.get("hearts") and isinstance(card_data["hearts"], dict):
            text = format_hearts(card_data["hearts"])
            embed.add_field(name="Hearts", value=text, inline=False)

        # Add Ability Text
        info_text = card_data.get("info_text")
        if info_text:
            text = "\n".join(info_text)

            # Replace keywords with emojis in the text
            # We use a regex with a callback to do this in a single pass,
            # which prevents "oops" where heart0 matches inside an already replaced heart01 tag.
            import re

            # Sort keys by length descending to ensure longer matches take precedence in the regex
            sorted_keys = sorted(emoji_map.keys(), key=len, reverse=True)
            pattern = re.compile("|".join(re.escape(k) for k in sorted_keys))

            def emoji_replacer(match):
                key = match.group(0)
                emoji_name = emoji_map[key]
                emoji = discord.utils.get(self.bot.emojis, name=emoji_name)
                return str(emoji) if emoji else f":{emoji_name}:"

            text = pattern.sub(emoji_replacer, text)

            # Discord field value limit is 1024 chars
            if len(text) > 1024:
                text = text[:1021] + "..."
            embed.add_field(name="Ability", value=text, inline=False)

        # Footer
        embed.set_footer(text=f"ID: {card_data['card_number']}")

        await interaction.followup.send(embed=embed)
