import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from cogs.market_ui import MarketView
import windtail_db as db

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
load_dotenv()
db.init_db()


@bot.event
async def on_ready():
    await bot.load_extension("cogs.market")
    bot.add_view(MarketView(bot))
    synced = await bot.tree.sync()
    print(f"Logged in as {bot.user}")


bot.run(os.environ.get("DISCORD_TOKEN"))
