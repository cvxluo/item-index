import discord
from discord.ext import commands


from Item import Item
from Book import Book

import datetime


from firebase_admin import db

# TODO: Remove this reinitialization system, relatively pointless
items = []
ref = db.reference('items')

for name, data in ref.get().items() :
    itemName = data['name'] if 'name' in data else "ERROR"
    itemURL = data['imageURL'] if 'imageURL' in data else None
    itemTags = data['tags'] if 'tags' in data else None
    items.append(Item(itemName, itemURL, itemTags))



class Trade:
    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True)
    async def addsell(self, ctx) :
        await self.bot.say("**`What is the name of the item you are selling?`**")
        item_name = await self.bot.wait_for_message(author = ctx.message.author)
        itemSearch = (item_name.content).lower().replace("'", "")

        found = False
        for item in items :
            if (itemSearch == item.getSearchTerm()) :
                self.bot.say("**`You are trying to sell: " + item.name + "`**")
                em = discord.Embed(title=item.name, color=1)

                for tagType, aTags in item.tags.items() :

                    tag = ', '.join(aTags)
                    em.add_field(name = tagType, value = tag, inline = False)

                if (item.imageURL) :
                    itemImage = str(item.imageURL)
                    em.set_image(url=itemImage)

                await self.bot.send_message(ctx.message.channel, embed = em)

                confirm_message = await self.bot.say("**`Is this correct?`**")

                OPTIONS = [
                    '\U00002705', # Check
                    '\U0000274c', # Cross
                ]

                for option in OPTIONS :
                    await self.bot.add_reaction(confirm_message, option)

                response = await self.bot.wait_for_reaction(OPTIONS, user = ctx.message.author, timeout=10.0, message = confirm_message)

                if response :
                    reacted_emoji = response.reaction.emoji

                    if reacted_emoji == '\U00002705' :
                        seller = ctx.message.author.name
                        await self.bot.say("**`Beginning a sell order for " + seller + " for " + item.name + "`**")
                        found = item
                        break


                    elif reacted_emoji == '\U0000274c' :
                        await self.bot.say("**`Canceling...`**")
                        return

                else :
                    await self.bot.say("**`Timed out...`**")
                    return


        item_selling = None
        if not found :
            await self.bot.say("**`Item not found, please try again`**")
            return

        else :
            item_selling = found



        cxp_emoji = None
        ccs_emoji = None

        for emoji in ctx.message.server.emojis :
            if emoji.name == "cxp" :
                cxp_emoji = emoji
            elif emoji.name == "ccs" :
                ccs_emoji = emoji



        currency_type_message = await self.bot.say("**`What currency are you selling this item for?`**")
        await self.bot.add_reaction(currency_type_message, cxp_emoji)
        await self.bot.add_reaction(currency_type_message, ccs_emoji)

        response = await self.bot.wait_for_reaction([cxp_emoji, ccs_emoji], user = ctx.message.author, timeout=10.0, message = currency_type_message)

        currency_type = ""
        if response :
            reacted_emoji = response.reaction.emoji

            if reacted_emoji == cxp_emoji :
                currency_type = "CXP"

            elif reacted_emoji == ccs_emoji :
                currency_type = "CCS"

        else :
            await self.bot.say("**`Timed out...`**")
            return



        await self.bot.say("**`How much " + currency_type + " are you selling " + item_selling.name + " for?`**")
        item_price = await self.bot.wait_for_message(author = ctx.message.author)

        try :
            item_price = int(item_price.content)
        except ValueError :
            await self.bot.say("**`Please enter a number.`**")
            return

        else :
            if (item_price <= 0) :
                await self.bot.say("**`Please enter a valid number.`**")
                return


        await self.bot.say("**`Selling " + item.name  + " for " + str(item_price) + " " + currency_type + "`**")



        confirm_message = await self.bot.say("**`Is this correct?`**")

        OPTIONS = [
            '\U00002705', # Check
            '\U0000274c', # Cross
        ]

        for option in OPTIONS :
            await self.bot.add_reaction(confirm_message, option)

        response = await self.bot.wait_for_reaction(OPTIONS, user = ctx.message.author, timeout=10.0, message = confirm_message)

        if response :
            reacted_emoji = response.reaction.emoji

            if reacted_emoji == '\U00002705' :
                ref.child(item_selling.name).child("trades").push().set({
                    'seller' : ctx.message.author.name,
                    'sellerID' : ctx.message.author.id,
                    'price' : item_price,
                    'currencyType' : currency_type,
                    'dateCreated' : str(datetime.datetime.now()),
                })
                await self.bot.say("**`Created a sell order for " + ctx.message.author.name + " of " + item_selling.name + " for " + str(item_price) + " " + currency_type + "`**")


            elif reacted_emoji == '\U0000274c' :
                await self.bot.say("**`Canceling...`**")

        else :
            await self.bot.say("**`Timed out...`**")




    @commands.command(pass_context=True)
    async def removesell(self, ctx) :
        await self.bot.say("**`What is the name of the item you were trying to sell?`**")
        item_name = await self.bot.wait_for_message(author = ctx.message.author)
        itemSearch = (item_name.content).lower().replace("'", "")

        found = False
        for item in items :
            if (itemSearch == item.getSearchTerm()) :
                self.bot.say("**`You were trying to sell: " + item.name + "`**")
                em = discord.Embed(title=item.name, color=1)

                for tagType, aTags in item.tags.items() :

                    tag = ', '.join(aTags)
                    em.add_field(name = tagType, value = tag, inline = False)

                if (item.imageURL) :
                    itemImage = str(item.imageURL)
                    em.set_image(url=itemImage)

                await self.bot.send_message(ctx.message.channel, embed = em)

                confirm_message = await self.bot.say("**`Is this correct?`**")

                OPTIONS = [
                    '\U00002705', # Check
                    '\U0000274c', # Cross
                ]

                for option in OPTIONS :
                    await self.bot.add_reaction(confirm_message, option)

                response = await self.bot.wait_for_reaction(OPTIONS, user = ctx.message.author, timeout=10.0, message = confirm_message)

                if response :
                    reacted_emoji = response.reaction.emoji

                    if reacted_emoji == '\U00002705' :
                        seller = ctx.message.author.name
                        await self.bot.say("**`Deleting all sell orders for " + seller + " for " + item.name + "`**")
                        found = item
                        break


                    elif reacted_emoji == '\U0000274c' :
                        await self.bot.say("**`Canceling...`**")
                        return

                else :
                    await self.bot.say("**`Timed out...`**")
                    return


        item_selling = None
        if not found :
            await self.bot.say("**`Item not found, please try again`**")
            return

        else :
            item_selling = found


        trades = ref.child(item_selling.name).child('trades').get()
        for trade in trades :
            if trades[trade]['sellerID'] == ctx.message.author.id :
                ref.child(item_selling.name).child('trades').child(trade).set({})




    @commands.command(pass_context=True)
    async def sells(self, ctx, *args) :
        itemSearch = ""
        if args :
            itemSearch = ' '.join(args).lower().replace("'", "")
        else :
            await self.bot.say("**`What is the name of the item you want to see orders for?`**")
            item_name = await self.bot.wait_for_message(author = ctx.message.author)
            itemSearch = (item_name.content).lower().replace("'", "")


        found = False
        for item in items :
            if (itemSearch == item.getSearchTerm()) :
                found = True

                trade_chapters = {}

                trades = ref.child(item.name).child('trades').get()
                if trades : # If any trades exist
                    for trade_name in trades :
                        trade = trades[trade_name]

                        try :
                            trade_chapters[str(trade['price'])].append(trade['seller']) # TODO: Make sure all seller names are updated to nicknames

                        except KeyError :
                            trade_chapters[str(trade['price']) + " " + trade['currencyType']] = [trade['seller']]


                    trade_book = Book(trade_chapters, "Orders for " + item.name, description = "Currently " + str(len(trades)) + " order for this item")


                    em = trade_book.get_current_page()
                    book_message = await self.bot.send_message(ctx.message.channel, embed = em)

                    OPTIONS = [
                        '\U000023ea', # Reverse
                        '\U00002b05', # Left Arrow
                        '\U000027a1', # Right Arrow
                        '\U000023e9', # Fast Forward
                    ]

                    for option in OPTIONS :
                        await self.bot.add_reaction(book_message, option)


                    response = await self.bot.wait_for_reaction(OPTIONS, user = ctx.message.author, timeout=10.0, message = book_message)

                    while response :
                        reacted_emoji = response.reaction.emoji

                        if reacted_emoji == '\U00002b05' :
                            trade_book.one_page_backward()

                        elif reacted_emoji == '\U000027a1' :
                            trade_book.one_page_forward()

                        elif reacted_emoji == '\U000023ea' :
                            trade_book.page_backward(5)

                        elif reacted_emoji == '\U000023e9' :
                            trade_book.page_forward(5)


                        new_embed = trade_book.get_current_page()
                        await self.bot.edit_message(book_message, embed = new_embed)
                        response = await self.bot.wait_for_reaction(OPTIONS, user = ctx.message.author, timeout=10.0, message = book_message)


                    else :
                        await self.bot.clear_reactions(book_message)

                else :
                    await self.bot.say("**`No orders found for " + item.name + "`**")


        if not found :
            await self.bot.say("**`Item not found, please try again`**")








def setup(bot):
    bot.add_cog(Trade(bot))
