import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from cogs.market_ui import MarketView
import windtail_db as db
from concurrent.futures import ThreadPoolExecutor


intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.cv_executor = ThreadPoolExecutor(max_workers=2)

load_dotenv()
db.init_db()


@bot.event
async def on_ready():
    await bot.load_extension("cogs.market")
    bot.add_view(MarketView(bot))
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


bot.run(os.environ.get("DISCORD_TOKEN"))
