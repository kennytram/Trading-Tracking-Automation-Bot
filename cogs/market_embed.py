# cogs/market_embed.py

import discord
import windtail_db as db
from utils.embed_utils import format_market_embed  # adjust if needed
# from windtail_config import ICON_URL


async def refresh_market_embed(
    bot: discord.Client,
    guild: discord.Guild,
    author_name: str = "System",
    is_daily: bool = False
):
    meta = db.get_market_meta(guild.id)
    if not meta:
        return

    try:
        channel = bot.get_channel(meta["channel_id"])
        if channel is None:
            return

        msg = await channel.fetch_message(meta["message_id"])
        prices = db.fetch_prices(guild.id)

        embed = format_market_embed(
            guild,
            prices,
            requester_name=author_name
        )

        if is_daily:
            embed.colour = discord.Color.orange()
            embed.set_footer(
                text="New trading day has begun",
                icon_url=ICON_URL
            )

        await msg.edit(embed=embed)

    except discord.NotFound:
        pass
    except discord.Forbidden:
        pass
