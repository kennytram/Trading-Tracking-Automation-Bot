import discord
import asyncio
from discord.ui import View, button, Modal, TextInput, Select, Button
import windtail_db as db
from cogs.market_embed import refresh_market_embed
import os

# OCR_NAME = os.environ.get('OCR_NAME')
# CURRENT_OCR_QUOTA = int(os.environ.get("CURRENT_OCR_QUOTA"))
# MIN_MARKET_PRICE_SCAN_ADDED = int(os.environ.get('MIN_MARKET_PRICE_SCAN_ADDED'))


# =============================
# PLAYER PAGINATION VIEW
# =============================
class PlayerPaginationView(View):
    def __init__(self, bot, guild_id, item_name, players, open_modal_callback):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild_id = guild_id
        self.item_name = item_name
        self.open_modal_callback = open_modal_callback

        # Paginate players
        self.pages = list(self.paginate(players))
        self.page_index = 0

        # Add select menu
        self.select = self.build_select(self.pages[self.page_index])
        self.add_item(self.select)

        # Add navigation buttons
        self.prev_button = Button(label="Prev", style=discord.ButtonStyle.gray)
        self.page_button = Button(label=f'{self.page_index + 1}/{len(self.pages)}', style=discord.ButtonStyle.gray, disabled=True)
        self.next_button = Button(label="Next", style=discord.ButtonStyle.gray)

        self.prev_button.callback = self.prev_page
        self.next_button.callback = self.next_page

        self.add_item(self.prev_button)
        self.add_item(self.page_button)
        self.add_item(self.next_button)

    def paginate(self, lst, page_size=25):
        """Split list into pages of 25"""
        for i in range(0, len(lst), page_size):
            yield lst[i:i + page_size]

    def build_select(self, player_page):
        select = Select(
            placeholder="Select a player",
            options=[discord.SelectOption(label=p["display"], value=str(p["display"])) for p in player_page],
            min_values=1,
            max_values=1
        )

        async def callback(interaction: discord.Interaction):
            player_id = str(select.values[0])
            await self.open_modal_callback(interaction, self.item_name, player_id)

        select.callback = callback
        return select

    async def update_select(self, interaction: discord.Interaction):
        """Update the select menu for the current page"""
        self.clear_items()
        self.select = self.build_select(self.pages[self.page_index])
        self.add_item(self.select)
        self.add_item(self.prev_button)
        self.page_button.label = f'{self.page_index + 1}/{len(self.pages)}'
        self.add_item(self.page_button)
        self.add_item(self.next_button)
        await interaction.edit_original_response(view=self)

    async def prev_page(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.page_index > 0:
            self.page_index -= 1
            await self.update_select(interaction)
        else:
            self.page_index = len(self.pages) - 1
            await self.update_select(interaction)
        # else:
        #     await interaction.response.defer()  # do nothing

    async def next_page(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.page_index < len(self.pages) - 1:
            self.page_index += 1
            await self.update_select(interaction)
        else:
            self.page_index = 0
            await self.update_select(interaction)
        # else:
        #     await interaction.response.defer()  # do nothing

# =============================
# DELETE PLAYER PAGINATION VIEW
# =============================

class DeletePlayerPaginationView(View):
    def __init__(self, bot, guild_id, players, open_callback):
        """
        bot: your bot instance
        guild_id: guild ID to fetch players from DB
        open_callback: coroutine to call when a player is selected. Signature: async def callback(interaction, player_id)
        """
        super().__init__(timeout=None)
        self.bot = bot
        self.guild_id = guild_id
        self.open_callback = open_callback

        # Each player will have 'player_display_name' and 'player_name' or 'id' for DB identification
        self.pages = list(self.paginate(players))
        self.page_index = 0

        # Add initial select menu
        self.select = self.build_select(self.pages[self.page_index])
        self.add_item(self.select)

        # Pagination buttons
        self.prev_button = Button(label="Prev", style=discord.ButtonStyle.gray)
        self.page_button = Button(label=f'{self.page_index + 1}/{len(self.pages)}', style=discord.ButtonStyle.gray, disabled=True)
        self.next_button = Button(label="Next", style=discord.ButtonStyle.gray)
        self.prev_button.callback = self.prev_page
        self.next_button.callback = self.next_page
        self.add_item(self.prev_button)
        self.add_item(self.page_button)
        self.add_item(self.next_button)

    def paginate(self, lst, page_size=25):
        """Split list into pages of 25"""
        for i in range(0, len(lst), page_size):
            yield lst[i:i + page_size]

    def build_select(self, player_page):
        select = Select(
            placeholder="Select a player to delete",
            options=[
                discord.SelectOption(label=p["display"], value=p["id"])
                for p in player_page
            ],
            min_values=1,
            max_values=1
        )

        async def callback(interaction: discord.Interaction):
            player_name = select.values[0]

            
            # Call the delete callback
            await self.open_callback(interaction, player_name)

        select.callback = callback
        return select

    async def update_select(self, interaction: discord.Interaction):
        """Refresh select menu for current page"""
        self.clear_items()
        self.select = self.build_select(self.pages[self.page_index])
        self.add_item(self.select)
        self.add_item(self.prev_button)
        self.page_button.label = f'{self.page_index + 1}/{len(self.pages)}'
        self.add_item(self.page_button)
        self.add_item(self.next_button)
        await interaction.edit_original_response(view=self)

    async def prev_page(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.page_index > 0:
            self.page_index -= 1
            await self.update_select(interaction)
        else:
            self.page_index = len(self.pages) - 1
            await self.update_select(interaction)
        # else:
        #     await interaction.response.defer()

    async def next_page(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.page_index < len(self.pages) - 1:
            self.page_index += 1
            await self.update_select(interaction)
        else:
            self.page_index = 0
            await self.update_select(interaction)
        # else:
        #     await interaction.response.defer()

class MarketView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)  # persistent
        self.bot = bot
        self.last_interaction_message = None

    async def delete_last_interaction(self):
        if self.last_interaction_message:
            try:
                await self.last_interaction_message.delete()
            except discord.NotFound:
                pass
            self.last_interaction_message = None

    async def select_item_then_player_delete(
        self,
        interaction: discord.Interaction,
        items,
        players,
        on_player_selected,  # callback(player_id, interaction)
        title: str
    ):
        # ITEM SELECT
        item_select = discord.ui.Select(
            placeholder="Select an item",
            options=[
                discord.SelectOption(
                    label=f"{i[0]} ({i[1]})",
                    value=i[0]
                )
                for i in items[:25]
            ]
        )

        async def item_callback(i_inter: discord.Interaction):
            selected_item = i_inter.data["values"][0]

            filtered_players = [p for p in players if p["item"] == selected_item]

            # PLAYER SELECT
            player_select = discord.ui.Select(
                placeholder="Select a player",
                options=[
                    discord.SelectOption(
                        label=p["player"],
                        value=str(p["player_name_id"])
                    )
                    for p in filtered_players[:25]
                ]
            )

            async def player_callback(p_inter: discord.Interaction):
                player_id = str(p_inter.data["values"][0])

                await on_player_selected(
                    player_id,
                    selected_item,
                    p_inter,
                    i_inter
                )

                # if p_inter.response.is_done():
                #     await i_inter.delete_original_response()

            player_select.callback = player_callback
            view = discord.ui.View(timeout=None)
            view.add_item(player_select)

            await i_inter.response.edit_message(
                content=f"**{selected_item}** → select a player:",
                view=view
            )

        item_select.callback = item_callback

        view = discord.ui.View(timeout=None)
        view.add_item(item_select)

        message = await interaction.followup.send(
            title,
            view=view,
            ephemeral=True,
            wait=True
        )
        return message



    # Add price
    @button(label="Add Price", style=discord.ButtonStyle.green, custom_id="market:add_price")
    async def add_price(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.delete_last_interaction()

        items = [{"item": i["item"], "keyword": i["item_keyword"]} for i in db.fetch_items()]
        # ITEM SELECT
        item_select = discord.ui.Select(
            placeholder="Select an item",
            options=[
                discord.SelectOption(
                    label=f"{i['item']} ({i['keyword']})",
                    value=i["item"]
                )
                for i in items[:25]
            ]
        )

        players = [
            {"display": p["display_player_name"], 
            "id": p["player_name"],
            "discord": p["discord"],
            } for p in db.fetch_players(interaction.guild.id)
        ]
        
        async def item_callback(i_inter: discord.Interaction):
            selected_item = i_inter.data["values"][0]
            
            async def open_modal_callback(interaction, item_name, player):
                await interaction.response.send_modal(AddPriceModal(self.bot, item_name, player))
                if interaction.response.is_done():
                    await interaction.delete_original_response()

            view = PlayerPaginationView(self.bot, i_inter.guild.id, selected_item, players, open_modal_callback)
            await i_inter.response.edit_message(content=f"**{selected_item}** → Select a player:", view=view)

        item_select.callback = item_callback
        view = View(timeout=None)
        view.add_item(item_select)

        await interaction.response.defer(ephemeral=True)
        self.last_interaction_message = await interaction.followup.send(
            "Select an item to add a price:",
            view=view,
            ephemeral=True,
            wait=True  # <-- returns actual Message object
        )

        # await interaction.response.send_message("Select an item to add a price:", view=view, ephemeral=True)

    # async def add_price_modal(self, interaction: discord.Interaction, item_name: str, players: list[tuple], player_name: str):
    #     player_id = next(pid for name, pid in players if name == player_name)
    #     await interaction.response.send_modal(AddPricePercentageModal(self.bot, item_name, player_name, player_id))

    # Delete price
    @button(label="Delete Price", style=discord.ButtonStyle.red, custom_id="market:delete_price")
    async def delete_price(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.delete_last_interaction()
        await interaction.response.defer(ephemeral=True)

        rows = db.fetch_prices(interaction.guild.id)
        items = sorted({
            (r["item"], r["item_keyword"])
            for r in rows
        })
        players = rows
        
        async def on_player(player_id, item, p_inter, i_inter):
            db.delete_price(interaction.guild.id, item, player_id)
            await refresh_market_embed(self.bot, interaction.guild, interaction.user.name)

            try:
                await i_inter.delete_original_response()
            except discord.NotFound:
                pass

            try:
                await p_inter.message.delete()
            except discord.NotFound:
                pass

            await p_inter.response.defer(ephemeral=True)
            msg = await p_inter.followup.send("Price deleted.", ephemeral=True, wait=True)
            await asyncio.sleep(3)
            await msg.delete()


        self.last_interaction_message = await self.select_item_then_player_delete(
            interaction,
            items=items,
            players=players, #should br rows
            on_player_selected=on_player,
            title="Select an item to delete a price:"
        )

    # Add player
    @button(label="Add Player", style=discord.ButtonStyle.blurple, custom_id="market:add_player")
    async def add_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.delete_last_interaction()

        await interaction.response.send_modal(AddPlayerModal(self.bot))

    # Delete player
    @button(label="Delete Player", style=discord.ButtonStyle.gray, custom_id="market:delete_player")
    async def delete_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.delete_last_interaction()

        players = [
            {"display": p["display_player_name"], 
            "id": p["player_name"],
            "discord": p["discord"],
            } for p in db.fetch_players(interaction.guild.id)
        ]

        async def delete_callback(interaction: discord.Interaction, player_name: str):
            # Delete player in DB
            db.delete_player(interaction.guild.id, player_name)
            await refresh_market_embed(self.bot, interaction.guild, interaction.user.name)
            await interaction.response.defer(ephemeral=True)  # acknowledge interaction
            await interaction.delete_original_response()
            msg = await interaction.followup.send(
                f"Player **{player_name}** removed.", ephemeral=True
            )
            await asyncio.sleep(3)
            await msg.delete()

        view = DeletePlayerPaginationView(self.bot, interaction.guild.id, players, delete_callback)
        
        # Defer first and send message as followup with wait=True to get Message object
        await interaction.response.defer(ephemeral=True)
        self.last_interaction_message = await interaction.followup.send(
            "Select a player to delete:",
            view=view,
            ephemeral=True,
            wait=True  # <-- returns actual Message object
        )
        
        
        # await interaction.response.send_message(
        #     "Select a player to delete:", view=view, ephemeral=True
        # )
    # @button(label="Scan Image", style=discord.ButtonStyle.green, custom_id="market:scan_image")
    # async def scan_image(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     # await self.delete_last_interaction()

    #     # await interaction.response.send_modal(ImageUploadModal(self.bot))

    #     await self.delete_last_interaction()
    #     await interaction.response.send_message(
    #         "Please upload the image in your next message.",
    #         ephemeral=True
    #     )

    #     def check(m):
    #         return (
    #             m.author == interaction.user
    #             and m.channel == interaction.channel
    #             and m.attachments
    #         )

    #     try:
    #         img_msg = await self.bot.wait_for("message", check=check, timeout=60)
    #         image = img_msg.attachments[0]

    #         # OCR logic here
    #         bot_wait_msg = await interaction.followup.send("Image received. Scanning…", ephemeral=True)

    #         try:
    #             current_rate = db.get_rate_limit(OCR_NAME)
    #             print(current_rate)
    #             if current_rate and current_rate["count"] < CURRENT_OCR_QUOTA:
    #                 db.increment_rate_limit(OCR_NAME)
    #             else:
    #                 msg = "Rate limit reached."
    #                 msg = await interaction.followup.send(msg)
    #                 await asyncio.sleep(3)
    #                 await msg.delete()
    #                 return
    #         except Exception as e:
    #             msg = str(e)
    #             msg = await interaction.followup.send(msg)
    #             await asyncio.sleep(3)
    #             await msg.delete()
    #             raise

    #         try:
    #             image_processor = self.bot.image_processor
    #             image_processor.set_image_url(image.url)
    #             image = await image_processor.read_image_from_url()
    #             best_item_detected, _, _ = image_processor.detect_item_with_regions(image)
    #             # result_pairs = await self.processor.scan_image_for_market_data()
    #             result_pairs = await image_processor.scan_image_for_market_data()
    #             if not result_pairs:
    #                 msg = await interaction.followup.send(
    #                     "No market data detected on this image.", ephemeral=True
    #                 )
    #                 await asyncio.sleep(3)
    #                 await msg.delete()
    #                 return
    #             elif len(result_pairs) == 1 and not result_pairs[0][0]:
    #                 uploader = db.fetch_player_by_discord(interaction.user.name)
    #                 percentage = result_pairs[0][1]
    #                 if uploader:
    #                     self.add(best_item_detected, percentage, uploader['name'])
    #                 else:
    #                     msg = await interaction.followup.send(
    #                     "Please add yourself to the player list with your discord handle first.", ephemeral=True
    #                     )
    #                     await asyncio.sleep(3)
    #                     await msg.delete()
    #             else:
    #                 player_names, percentages = zip(*result_pairs)
    #                 db.add_many_scanned_players(interaction.guild.id, player_names)
    #                 db.upsert_many_prices(interaction.guild.id, best_item_detected, player_names, percentages, MIN_MARKET_PRICE_SCAN_ADDED)
    #                 await refresh_market_embed(self.bot, interaction.guild.id, interaction.user.name)
    #                 msg = "Prices added."
    #                 msg = await interaction.followup.send(msg, ephemeral=True)
    #                 await asyncio.sleep(3)
    #                 await msg.delete()
                    
    #         except Exception as e:
    #             msg = "Scanning errors. Please try again later."
    #             msg = await interaction.followup.send(msg, ephemeral=True)
    #             await asyncio.sleep(3)
    #             await msg.delete()
                    

    #     except asyncio.TimeoutError:
    #         await interaction.followup.send("Timed out waiting for image.", ephemeral=True)

    #     await img_msg.delete()
    #     await bot_wait_msg.delete()

class AddPriceModal(Modal, title="Add Price"):
    percentage = TextInput(label="Percentage (e.g. 213)")

    def __init__(self, bot, item_name, player):
        super().__init__()
        self.bot = bot
        self.item_name = item_name
        self.player = player
        self.title += f"— {item_name} — {player}"
        
    async def on_submit(self, interaction: discord.Interaction):
        try:
            db.upsert_price(
                interaction.guild.id,
                self.item_name,
                self.player.lower(),
                int(self.percentage.value)
            )
            await refresh_market_embed(self.bot, interaction.guild, interaction.user.name)
            msg = "Price added."
        except db.ItemNotFound:
            msg = f"Item **{self.item_name}** not found."
        except db.PlayerNotFound:
            msg = f"Player **{self.player}** not found."
        except ValueError:
            msg = "Please enter a valid value for percentage."
        except Exception as e:
            msg = str(e)
        await interaction.response.send_message(msg, ephemeral=True, delete_after=3)


# class DeletePriceModal(Modal, title="Delete Price"):
#     player = TextInput(label="Player name")

#     def __init__(self, bot, item_name):
#         super().__init__()
#         self.bot = bot
#         self.item_name = item_name
#         self.title += f" ({item_name})"

#     async def on_submit(self, interaction: discord.Interaction):
#         try:
#             db.delete_price(interaction.guild.id, self.item_name, self.player.value.lower())
#             await refresh_market_embed(self.bot, interaction.guild, interaction.user.name)
#             msg = "Price deleted."
#         except db.ItemNotFound:
#             msg = f"Item **{self.item_name}** not found."
#         except db.PlayerNotFound:
#             msg = f"Player **{self.player.value}** not found."
#         except ValueError:
#             msg = "Please enter valid values."
#         except Exception as e:
#             msg = str(e)
#             raise
#         await interaction.response.send_message(msg, ephemeral=True, delete_after=3)


class AddPlayerModal(Modal, title="Add Player"):
    name = TextInput(label="Player name")
    discord_handle = TextInput(label="Discord username (optional)", required=False)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        db.add_player(interaction.guild.id, self.name.value, self.discord_handle.value or None)
        # await refresh_market_embed(self.bot, interaction.guild, interaction.user.name)
        await interaction.response.send_message(f"Player **{self.name.value}** added.", ephemeral=True, delete_after=3)


# class DeletePlayerModal(Modal, title="Delete Player"):
#     name = TextInput(label="Player name")

#     def __init__(self, bot):
#         super().__init__()
#         self.bot = bot

#     async def on_submit(self, interaction: discord.Interaction):
#         try:
#             db.delete_player(interaction.guild.id, self.name.value)
#             await refresh_market_embed(self.bot, interaction.guild, interaction.user.name)
#             msg = f"{self.name.value} removed."
#         except db.PlayerNotFound:
#             msg = f"Player **{self.name.value}** not found."
#         except Exception as e:
#             msg = str(e)
#             raise
#         await interaction.response.send_message(msg, ephemeral=True, delete_after=3)


# Not supported until 2.7 (currently 2.6.4)
# class ImageUploadModal(Modal, title="Upload Your Image"):
#     image = FileUpload()

#     def __init__(self, bot):
#         super().__init__()
#         self.bot = bot

#     async def on_submit(self, interaction: discord.Interaction):
#         # Get the uploaded file
#         files = interaction.files  # List of uploaded files
#         if files:
#             file = files[0]
#             # Save or process the file
#             await interaction.response.send_message(f"Received: {file.filename}", ephemeral=True)
#         else:
#             await interaction.response.send_message("No file uploaded.", ephemeral=True)