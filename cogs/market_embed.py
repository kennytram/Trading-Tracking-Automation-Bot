# cogs/market_embed.py

import discord
import os
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
    
    channel = bot.get_channel(meta["channel_id"])
    if channel is None:
        print(f"Channel {meta['channel_id']} not found.")
        return
    try:
        msg = await channel.fetch_message(meta["message_id"])
    except discord.NotFound:
        print(f"Message not found.")

    except discord.Forbidden:
        print(f"No permission to access channel {channel.id}")
        return
    except discord.HTTPException as e:
        print(f"HTTP error fetching message: {e}")
        return
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
            icon_url=os.environ.get("ICON_URL")
        )

    try:
        await msg.edit(embed=embed)
    except discord.Forbidden:
        print(f"No permission to edit message {msg.id} in channel {channel.id}")
    except discord.HTTPException as e:
        print(f"Failed to edit market message {msg.id}: {e}")
