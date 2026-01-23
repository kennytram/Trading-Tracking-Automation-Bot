import discord
import os
import asyncio
from discord.ext import commands, tasks
from datetime import datetime, timezone, time as dtime
from collections import defaultdict

import windtail_db as db
from utils.image_utils import ImageProcessor
from utils.embed_utils import format_market_embed
from cogs.market_ui import MarketView
from cogs.market_embed import refresh_market_embed
# from windtail_config import ICON_URL

RESET_HOUR_UTC = int(os.environ.get("RESET_HOUR_UTC"))
OCR_NAME = os.environ.get("OCR_NAME")
CURRENT_OCR_QUOTA = int(os.environ.get("CURRENT_OCR_QUOTA"))
MIN_MARKET_PRICE_SCAN_ADDED = int(os.environ.get('MIN_MARKET_PRICE_SCAN_ADDED'))

class Market(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        if not hasattr(bot, "image_processor"):
            bot.image_processor = ImageProcessor()
        self.processor = bot.image_processor
        self.daily_reset.start()
        self.monthly_reset.start()
    
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
    # MARKET COMMAND
    # ======================================================
    @commands.hybrid_command()
    async def market(self, ctx: commands.Context):
        """Create a new market post and delete all previous ones."""

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
                    pass
                    # print("Missing permissions to delete old market")
                except discord.HTTPException as e:
                    pass
                    # print("Failed deleting old market:", e)

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
    async def add(
        self,
        ctx: commands.Context,
        item: str,
        percentage: int,
        player: str
    ):
        """Add a new market price to the market post."""
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
    async def delete(self, ctx: commands.Context, item: str, player: str):
        """Delete a market price from the market post."""
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
        discord_handle = None
    ):
        """Add a new player to the market system."""
        db.add_player(ctx.guild.id, name, discord_handle)
        # await refresh_market_embed(self.bot, ctx.guild, ctx.author.name)
        await self._respond(ctx, f"**{name}** added.")

    # ======================================================
    # DELETE PLAYER
    # ======================================================
    @commands.hybrid_command()
    async def deleteplayer(self, ctx: commands.Context, name: str):
        """Delete a player from the market system."""
        try:
            db.delete_player(ctx.guild.id, name)
            await refresh_market_embed(self.bot, ctx.guild, ctx.author.name)
            msg = f"**{name}** deleted."

        except db.PlayerNotFound:
            msg = f"Player **{name}** not found."

        await self._respond(ctx, msg)

    # ======================================================
    # SCAN IMAGE FOR PRICES
    # =====================================================
    @commands.hybrid_command()
    async def scanimage(
        self,
        ctx: commands.Context
    ):
        """Scan an image for market prices and add them to the market post."""
        msg = ""
        if not ctx.message.attachments:
            msg = "Please attach an image to scan."
        elif len(ctx.message.attachments) > 1:
            msg = "Please attach one image at a time."

        attachment = ctx.message.attachments[0]
        if not any(attachment.filename.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg")):
            msg = "Only image attachments are supported (.png, .jpg, .jpeg)."
        
        if msg:
            await self._respond(ctx, msg)
            return
        else:
            try:
                current_rate = db.get_rate_limit(OCR_NAME)
                if current_rate and current_rate["count"] < CURRENT_OCR_QUOTA:
                    db.increment_rate_limit(OCR_NAME)
                else:
                    msg = "Rate limit reached."
                    await self._respond(ctx, msg)
                    return
            except Exception as e:
                msg = str(e)
                raise
            
            try:
                self.processor.set_image_url(attachment.url)
                image = await self.processor.read_image_from_url()
                best_item_detected, _, _ = self.processor.detect_item_with_regions(image)
                # result_pairs = await self.processor.scan_image_for_market_data()
                result_pairs = await self.processor.scan_image_for_market_data()
                if not result_pairs:
                    msg = "No market data detected on this image."
                    await self._respond(ctx, msg)
                    return
                elif len(result_pairs) == 1 and not result_pairs[0][0]:
                    uploader = db.fetch_player_by_discord(ctx.guild.id, ctx.author.name)
                    percentage = result_pairs[0][1]
                    if uploader:
                        db.upsert_price(ctx.guild.id, best_item_detected, uploader['player_name'], percentage)
                        await refresh_market_embed(self.bot, ctx.guild, ctx.author.name)
                        msg = "Price added."
                    else:
                        msg = "Please add yourself to the player list with your discord handle first."
                else:
                    player_names, percentages = zip(*result_pairs)
                    db.add_many_scanned_players(ctx.guild.id, player_names)
                    db.upsert_many_prices(ctx.guild.id, best_item_detected, player_names, percentages, MIN_MARKET_PRICE_SCAN_ADDED)
                    await refresh_market_embed(self.bot, ctx.guild, ctx.author.name)
                    msg = "Prices added."
                    
            except Exception as e:
                msg = "Scanning errors. Please try again later."

        await self._respond(ctx, msg)

    # ======================================================
    # DAILY RESET TASK
    # ======================================================
    @tasks.loop(time=dtime(hour=0, minute=40, tzinfo=timezone.utc))
    async def daily_reset(self):
        db.reset_market_prices()

        for guild in self.bot.guilds:
            await refresh_market_embed(self.bot, guild, is_daily=True)


    # ======================================================
    # MONTHLY RESET TASK
    # ======================================================
    @tasks.loop(time=dtime(hour=RESET_HOUR_UTC, tzinfo=timezone.utc))
    async def monthly_reset(self):
        now = datetime.now(timezone.utc)

        if now.day != 1:
            return
        db.reset_rate_limits(OCR_NAME)

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
