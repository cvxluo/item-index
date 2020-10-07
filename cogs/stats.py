import discord
from discord.ext import commands

from firebase_admin import firestore


class Stats (commands.Cog):
    def __init__(self, bot):
        db = firestore.client()
        self.bot = bot
        self.stat_ref = db.collection('stats')

    @commands.command()
    async def stats(self, ctx, *args) :

        em = discord.Embed(title="**Monumenta Item Index Bot - Statistics**", color=1)

        discord_stat_dict = self.stat_ref.document('discord').get().to_dict()
        itemFail = discord_stat_dict['itemFail']
        itemFound = discord_stat_dict['itemFound']
        itemlist = discord_stat_dict['itemlist']
        search = discord_stat_dict['search']
        tagSearch = discord_stat_dict['tagSearch']

        discord_stats = "**Items Found** - " + str(itemFound) + "\n"
        discord_stats += "**Failed to Find** - " + str(itemFail) + "\n"
        discord_stats += "**Item List Called** - " + str(itemlist) + "\n"
        discord_stats += "**Searches Performed** - " + str(search) + "\n"
        discord_stats += "**Tag Searches Performed** - " + str(tagSearch) + "\n"

        website_stat_dict = self.stat_ref.document('website').get().to_dict()
        visits = website_stat_dict['visits']

        website_stats = "**Visits** - " + str(visits) + "\n"

        em.add_field(name = "**Discord**", value = discord_stats)
        em.add_field(name = "**Website**", value = website_stats)

        em.set_footer(text = "Note that these statistics are collected anonymously and may not be accurate.")

        await ctx.channel.send(embed = em)

    @commands.command()
    async def resetstats(self, ctx, *args) :

        admins = ["140920560610836480"]  # Vex
        if ctx.author.id in admins :
            confirm_message = await ctx.channel.send_message(ctx.message.channel, "Are you sure?")
            await self.bot.add_reaction(confirm_message, '1⃣')
            await self.bot.add_reaction(confirm_message, '🅾')

            response = await self.bot.wait_for_reaction(['1⃣', '🅾'], user = ctx.author, timeout=10.0, message = confirm_message)

            if response :  # If timeout, response will be None
                reacted_emoji = response.reaction.emoji

                if reacted_emoji == "1⃣" :
                    await ctx.channel.send('Resetting stats...')
                    self.stat_ref.document('discord').set({
                        'itemFail' : 0,
                        'itemFound' : 0,
                        'itemlist' : 0,
                        'search' : 0,
                        'tagSearch' : 0,
                    })
                    await ctx.channel.send("Done!")

                else :
                    await ctx.channel.send("Aborted!")

            else :
                await ctx.channel.send("**`Timed out...`**")
                return

        else :
            await ctx.channel.send("Not verified!")


def setup(bot):
    bot.add_cog(Stats(bot))
