import discord
from discord.ext import commands


class Help (commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, *args) :

        # TODO : Write more specific command descriptions for each command

        em = discord.Embed(title="**Monumenta Item Index Bot - Command Reference**", color=1)

        em.add_field(name = "**General**", value = """
        ***!help*** - shows this command
        ***!changelog*** - (not working right now) view the changelog for the item index
        ***!stats*** - shows some various stats about the item index
        ***!contribute*** - view links to code behind bot and website
        """)

        em.add_field(name = "**Items**", value = """
        ***!item [item name]*** - retrieves an item from the index
        ***!itemlist*** - retrieves every item from the index
        ***!tag*** - searches the item index by tag
        ***!search [query]*** - searches the item index with a general query
        """)

        em.add_field(name = "**Trade**", value = """
        NOTE - TEMPORARILY DISABLED
        ***!addsell*** - begins the process of creating a sell order for an item
        ***!removesell*** - begins the process of deleting all your sell orders for an item
        ***!sells ![item name]*** - retrieves all the sell orders for an item
        """)

        em.add_field(name = "**Kaul**", value = """
        ***!rank*** - gives you the Kaul role
        ***!derank*** - removes the Kaul role from you
        ***!kaultime [time]*** - pings everyone with the Kaul role - with the time argument, specifies when Kaul will spawn
        """)

        em.add_field(name = "**Wiki**", value = """
        ***!wiki [wiki page]*** - retrieves a page from the wiki
        """)

        em.set_footer(text = "Brackets indicate a place for you to put an argument (without the brackets) - ! indicates the argument is optional")

        await ctx.channel.send(embed = em)

    @commands.command()
    async def changelog(self, ctx) :

        # TODO: finish this when rewrite is done

        em = discord.Embed(title="**Monumenta Item Index Bot**", color=1)
        em.add_field(name = "**Changelog**", value = """
        """)

        await ctx.channel.send(embed = em)

    @commands.command()
    async def contribute(self, ctx) :

        em = discord.Embed(title="**Monumenta Item Index Bot**", color=1)
        em.add_field(name = "**Contribute**", value = """
        Both the Discord bot and website are open source:
        [Bot code](https://github.com/cvxluo/item-index)
        [Website code](https://github.com/cvxluo/item-index-website)
        Currently maintained by <@140920560610836480>
        Open to contribution, feel free to make a pull request or issue!
        """)

        await ctx.channel.send(embed = em)


def setup(bot):
    bot.add_cog(Help(bot))
