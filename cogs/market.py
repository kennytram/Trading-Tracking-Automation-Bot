import discord
import os
from discord.ext import commands, tasks
from datetime import timezone, time as dtime
from collections import defaultdict

import windtail_db as db
from utils.embed_utils import format_market_embed
from cogs.market_ui import MarketView
from cogs.market_embed import refresh_market_embed
# from windtail_config import ICON_URL

RESET_HOUR_UTC = int(os.environ.get("RESET_HOUR_UTC"))

class Market(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.daily_reset.start()
    
    # ======================================================
    # Error Handler
    # ======================================================

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.HybridCommandError):
            error = error.original

        if isinstance(error, commands.MissingRequiredArgument):
            msg = f"Usage: `{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}`"
            await self._respond(ctx, msg)
            return

    # ======================================================
    # AUTOCOMPLETE
    # ======================================================

    # async def player_autocomplete(
    #     self,
    #     interaction: discord.Interaction,
    #     current: str
    # ):
    #     rows = db.fetch_prices(interaction.guild.id)
    #     return [
    #         discord.app_commands.Choice(
    #             name=p["display_player_name"],
    #             value=p["player_name"]
    #         )
    #         for p in rows
    #         if current.lower() in p["player_name"].lower()
    #     ][:25]

    # async def item_autocomplete(
    #     self,
    #     interaction: discord.Interaction,
    #     current: str
    # ):
    #     rows = db.fetch_prices(interaction.guild.id)
    #     return [
    #         discord.app_commands.Choice(
    #             name=i["item"],
    #             value=i["item"]
    #         )
    #         for i in rows
    #         if current.lower() in i["item"].lower()
    #     ][:25]

    # ======================================================
    # MARKET COMMAND
    # ======================================================
    @commands.hybrid_command()
    async def market(self, ctx: commands.Context):
        """Create a NEW market post and delete all previous ones."""

        prices = db.fetch_prices(ctx.guild.id)
        embed = format_market_embed(ctx.guild, prices, ctx.author.name)
        view = MarketView(self.bot)

        # ==========================
        # DELETE OLD MARKET POSTS
        # ==========================
        meta = db.get_market_meta(ctx.guild.id)

        if meta:
            channel = self.bot.get_channel(meta["channel_id"])
            if channel:
                try:
                    old_msg = await channel.fetch_message(meta["message_id"])
                    await old_msg.delete()
                except discord.NotFound:
                    pass
                except discord.Forbidden:
                    print("Missing permissions to delete old market")
                except discord.HTTPException as e:
                    print("Failed deleting old market:", e)

        # ==========================
        # CREATE NEW MARKET POST
        # ==========================
        msg = await ctx.send(embed=embed, view=view)
        await msg.pin()

        # Delete the system pin message
        async for m in ctx.channel.history(limit=5):
            if m.type == discord.MessageType.pins_add:
                await m.delete()
                break

        db.set_market_meta(ctx.guild.id, ctx.channel.id, msg.id)

        # ==========================
        # CLEANUP / RESPONSE
        # ==========================
        if ctx.message:
            # prefix command
            await ctx.message.delete()

        elif ctx.interaction:
            # slash command must respond
            await ctx.interaction.response.send_message(
                "📌 New market post created.",
                ephemeral=True
            )


    # ======================================================
    # ADD PRICE
    # ======================================================
    @commands.hybrid_command()
    # @discord.app_commands.autocomplete(
    #     item=item_autocomplete,
    #     player=player_autocomplete
    # )
    async def add(
        self,
        ctx: commands.Context,
        item: str,
        percentage: int,
        player: str
    ):
        try:
            db.upsert_price(ctx.guild.id, item, player.lower(), percentage)
            await refresh_market_embed(self.bot, ctx.guild, ctx.author.name)
            msg = "Price added."

        except db.ItemNotFound as e:
            msg = f"Item **{item}** not found."
        except db.PlayerNotFound as e:
            msg = f"Player **{player}** not found."
        except ValueError:
            msg = "Please enter valid values."
        except Exception as e:
            msg = str(e)
            raise

        await self._respond(ctx, msg)

    # ======================================================
    # DELETE PRICE
    # ======================================================
    @commands.hybrid_command()
    # @discord.app_commands.autocomplete(
    #     item=item_autocomplete,
    #     player=player_autocomplete
    # )
    async def delete(self, ctx: commands.Context, item: str, player: str):
        try:
            db.delete_price(ctx.guild.id, item, player.lower())
            await refresh_market_embed(self.bot, ctx.guild, ctx.author.name)
            msg = "Price deleted."

        except db.ItemNotFound:
            msg = f"Item **{item}** not found."
        except db.PlayerNotFound:
            msg = f"Player **{player}** not found."
        except ValueError:
            msg = "Please enter valid values."
        except Exception as e:
            msg = str(e)
            raise

        await self._respond(ctx, msg)

    # ======================================================
    # ADD PLAYER
    # ======================================================
    @commands.hybrid_command()
    async def addplayer(
        self,
        ctx: commands.Context,
        name: str,
        discord_handle: str | None = None
    ):
        db.add_player(ctx.guild.id, name, discord_handle)
        # await refresh_market_embed(self.bot, ctx.guild, ctx.author.name)
        await self._respond(ctx, f"**{name}** added.")

    # ======================================================
    # DELETE PLAYER
    # ======================================================
    @commands.hybrid_command()
    # @discord.app_commands.autocomplete(name=player_autocomplete)
    async def deleteplayer(self, ctx: commands.Context, name: str):
        try:
            db.delete_player(ctx.guild.id, name)
            await refresh_market_embed(self.bot, ctx.guild, ctx.author.name)
            msg = f"**{name}** deleted."

        except db.PlayerNotFound:
            msg = f"Player **{name}** not found."

        await self._respond(ctx, msg)

    # ======================================================
    # DAILY RESET TASK
    # ======================================================
    @tasks.loop(time=dtime(hour=RESET_HOUR_UTC, tzinfo=timezone.utc))
    async def daily_reset(self):
        db.reset_market_prices()

        for guild in self.bot.guilds:
            await refresh_market_embed(self.bot, guild, is_daily=True)
            

    # ======================================================
    # RESPONSE HELPER
    # ======================================================
    async def _respond(self, ctx: commands.Context, msg: str):
        if ctx.interaction:
            await ctx.interaction.response.send_message(
                msg, ephemeral=True, delete_after=3
            )
        else:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete(delay=3)


async def setup(bot):
    await bot.add_cog(Market(bot))
