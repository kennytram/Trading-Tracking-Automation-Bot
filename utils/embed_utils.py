import discord
import math
from datetime import datetime, timezone
from collections import defaultdict

from utils.time_utils import (
    next_reset_today_or_tomorrow,
    next_weekday_at_hour,
    next_thursday_and_sunday
)
# from windtail_config import RESET_HOUR_UTC, ICON_URL


def format_market_embed(guild, rows, requester_name="System"):
    now = datetime.now(timezone.utc)

    unix_today_reset = next_reset_today_or_tomorrow(os.environ.get('RESET_HOUR_UTC'))
    unix_thursday, unix_sunday = next_thursday_and_sunday(os.environ.get(R'ESET_HOUR_UTC'))

    embed = discord.Embed(
        title="Where Winds Meet Market Trades",
        colour=discord.Color.green(),
        timestamp=now
    )

    embed.description = "\n".join([
        f"Daily reset for market prices occurs at <t:{unix_today_reset}:t>",
        f"Stock resets on <t:{unix_thursday}:F> and <t:{unix_sunday}:F>",
        f"New market fluctuations occur on <t:{unix_thursday}:F>",
        ""
    ])
    
    embed.set_footer(
        text=f"Updated by {requester_name}",
        icon_url=(os.environ.get('ICON_URL'))
    )

    if not rows:
        embed.colour = discord.Color.orange()
        embed.description += "\nMarket is currently empty."
        return embed

    grouped = defaultdict(list)
    for r in rows:
        grouped[r["item"].lower()].append(r)

    for key in sorted(grouped):
        item_rows = grouped[key][:8]
        item = item_rows[0]["item"]
        price_lines = []
        value_lines = []

        for r in item_rows:
            name = r["player"]
            if r["discord"]:
                member = discord.utils.get(guild.members, name=r["discord"])
                if member:
                    name += f" (<@{member.id}>)"

            base_price_percentage = r['price'] * (r['percentage']+100)/100
            base_tax_rate = 0.89
            guild_bonus_rates = 0.99 * 1.145
            trade_price = math.ceil(base_price_percentage * base_tax_rate)
            guild_trade_price = math.ceil(base_price_percentage * guild_bonus_rates)
            
            #max character limit per price_line is 73
            max_character_limit_price_line = 73
            price_line_value = f"> `{r['percentage']}%` — {name}"
            length_price_line_value = len(price_line_value)

            chunks = f"`{trade_price} ({guild_trade_price})`" + '\n' * (length_price_line_value // max_character_limit_price_line)

            price_lines.append(price_line_value)
            value_lines.append(chunks)

        embed.add_field(name=item, value="\n".join(price_lines), inline=True)
        embed.add_field(name="Prices 🪙", value="\n".join(value_lines), inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
    embed.colour = 0x00B0F4
    return embed
