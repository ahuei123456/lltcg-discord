import logging
import re
from pathlib import Path
from urllib.parse import quote

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from src import config
from src.db.card_repository import CardData, CardRepository

_log = logging.getLogger(__name__)


class CardLookup(commands.Cog):
    def __init__(self, bot: commands.Bot, card_repo: CardRepository):
        self.bot = bot
        self.card_repo = card_repo
        # Retrieve image cache path from centralized config
        settings = config.get_config()
        self.img_cache_dir = Path(settings.get("IMAGE_CACHE_PATH", "data/images"))

        # heart types -> emoji names mapping
        self.emoji_map = {
            "heart01": "heart01",  # Pink
            "heart02": "heart02",  # Red
            "heart03": "heart03",  # Yellow
            "heart04": "heart04",  # Green
            "heart05": "heart05",  # Blue
            "heart06": "heart06",  # Purple
            "heart0": "heart00",  # Grey
            "ALL1": "sp_all",  # All (Blade Heart generic)
            "b_heart01": "blade_heart01",
            "b_heart02": "blade_heart02",
            "b_heart03": "blade_heart03",
            "b_heart04": "blade_heart04",
            "b_heart05": "blade_heart05",
            "b_heart06": "blade_heart06",
            "ALL": "sp_all",  # Variant
            "ドロー": "sp_draw",
            "スコア": "sp_score",
        }

    async def _get_or_download_image(
        self, series: str, product: str, number_str: str, rarity: str, img_url: str | None
    ) -> discord.File | None:
        """Checks local cache for image, downloads if missing, and returns discord.File."""
        if not img_url:
            return None

        # Build local path
        safe_series = series.replace("!", "SP")
        safe_rarity = rarity.replace("+", "plus")
        filename = f"{safe_series}-{product}-{number_str}-{safe_rarity}.png"
        local_path = self.img_cache_dir / filename

        # Download if missing
        if not local_path.exists():
            try:
                # Ensure directory exists
                self.img_cache_dir.mkdir(parents=True, exist_ok=True)

                # Encode URL
                proto, rest = img_url.split("://", 1)
                parts = rest.split("/", 1)
                if len(parts) == 2:
                    domain, path = parts
                    encoded_path = quote(path, safe="/:?=&!")
                    download_url = f"{proto}://{domain}/{encoded_path}"

                    headers = {
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/91.0.4472.124 Safari/537.36"
                        )
                    }
                    async with aiohttp.ClientSession() as session, session.get(download_url, headers=headers) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            with open(local_path, "wb") as f:
                                f.write(data)
                            _log.info(f"Cached image: {local_path.name}")
                        else:
                            _log.error(f"Download failed for {download_url}: {resp.status}")
            except Exception as e:
                _log.error(f"Image download error: {e}")

        # Return file if exists
        if local_path.exists():
            return discord.File(local_path, filename="image.png")
        return None

    def _format_hearts(self, hearts_data: dict[str, str]) -> str:
        """Formats a heart dictionary into an emoji string."""
        parts = []
        for key, amount in hearts_data.items():
            emoji_name = self.emoji_map.get(key, key)
            emoji = discord.utils.get(self.bot.emojis, name=emoji_name)
            display_emoji = str(emoji) if emoji else f":{emoji_name}:"
            parts.append(f"{display_emoji} {amount}")
        return "   ".join(parts)

    def _apply_ability_emojis(self, text: str) -> str:
        """Replaces keywords in ability text with emojis using single-pass regex."""
        sorted_keys = sorted(self.emoji_map.keys(), key=len, reverse=True)
        pattern = re.compile("|".join(re.escape(k) for k in sorted_keys))

        def emoji_replacer(match):
            key = match.group(0)
            emoji_name = self.emoji_map[key]
            emoji = discord.utils.get(self.bot.emojis, name=emoji_name)
            return str(emoji) if emoji else f":{emoji_name}:"

        return pattern.sub(emoji_replacer, text)

    def _build_card_embed(self, card_data: CardData) -> discord.Embed:
        """Constructs the rich embed for a card."""
        embed = discord.Embed(
            title=f"{card_data['name']} ({card_data['rarity']})",
            description=f"**Set**: {card_data['set']}\n**Type**: {card_data['card_type']}",
            color=discord.Color.blue(),
        )

        # Basic Fields
        if card_data.get("unit"):
            embed.add_field(name="Unit", value=card_data["unit"], inline=True)
        if card_data.get("group"):
            embed.add_field(name="Group", value=", ".join(card_data["group"]), inline=True)
        if card_data.get("cost"):
            embed.add_field(name="Cost", value=card_data["cost"], inline=True)
        if card_data.get("score"):
            embed.add_field(name="Score", value=card_data["score"], inline=True)

        # Heart Stats
        required_hearts = card_data.get("required_hearts")
        if required_hearts:
            text = self._format_hearts(required_hearts)
            embed.add_field(name="Required Hearts", value=text, inline=False)

        # Blade Heart Logic
        blade_parts = []
        blade_hearts = card_data.get("blade_hearts")
        if blade_hearts:
            blade_parts.append(self._format_hearts(blade_hearts))

        special_hearts = card_data.get("special_hearts")
        if special_hearts:
            emoji_name = self.emoji_map.get(special_hearts)
            emoji = discord.utils.get(self.bot.emojis, name=emoji_name) if emoji_name else None
            blade_parts.append(str(emoji) if emoji else (f":{emoji_name}:" if emoji_name else special_hearts))

        if blade_parts:
            embed.add_field(name="Blade Heart", value="   ".join(blade_parts), inline=False)

        hearts = card_data.get("hearts")
        if hearts:
            text = self._format_hearts(hearts)
            embed.add_field(name="Hearts", value=text, inline=False)

        # Ability Text
        info_text = card_data.get("info_text")
        if info_text:
            text = "\n".join(info_text)
            text = self._apply_ability_emojis(text)
            if len(text) > 1024:
                text = text[:1021] + "..."
            embed.add_field(name="Ability", value=text, inline=False)

        embed.set_footer(text=f"ID: {card_data['card_number']}")
        return embed

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

        number_str = f"{number:03d}"
        card_data = self.card_repo.get_card(series, product, number_str, rarity)

        if not card_data:
            await interaction.followup.send(
                f"Card not found: `{series}-{product}-{number_str}-{rarity}`.",
                ephemeral=True,
            )
            return

        # Prepare Embed
        embed = self._build_card_embed(card_data)

        # Prepare Image
        file = await self._get_or_download_image(series, product, number_str, rarity, card_data.get("img_url"))
        if file:
            embed.set_image(url="attachment://image.png")

        # Send
        await interaction.followup.send(embed=embed, file=file) if file else await interaction.followup.send(
            embed=embed
        )
