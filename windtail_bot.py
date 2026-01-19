import discord
from discord.ext import commands
# from windtail_config import DISCORD_TOKEN
from dotenv import load_dotenv
import os
from cogs.market_ui import MarketView
import windtail_db as db

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
db.init_db()
load_dotenv()

@bot.event
async def on_ready():
    await bot.load_extension("cogs.market")
    bot.add_view(MarketView(bot))


    guild = discord.Object(id=784731196117876756)
    bot.tree.copy_global_to(guild=guild)
    synced = await bot.tree.sync(guild=guild)

    # synced = await bot.tree.sync()


    print(f"Logged in as {bot.user}")
    print(f"Synced {len(synced)} commands")

bot.run(os.environ.get('DISCORD_TOKEN'))
