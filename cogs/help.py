import discord
from discord.ext import commands


class Help:
    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True)
    async def help(self, ctx, *args) :

        # TODO : Write more specific command descriptions for each command

        em = discord.Embed(title="**Monumenta Item Index Bot - Command Reference**", color=1)

        em.add_field(name = "**General**", value =
        """
        ***!help*** - shows this command
        """)

        em.add_field(name = "**Items**", value =
        """
        ***!item [item name]*** - retrieves an item from the index
        ***!itemlist*** - retrieves every item from the index
        ***!tag*** - searches the item index by tag
        """)

        em.add_field(name = "**Trade**", value =
        """
        ***!addsell*** - begins the process of creating a sell order for an item
        ***!removesell*** - begins the process of deleting all your sell orders for an item
        ***!sells ![item name]*** - retrieves all the sell orders for an item
        """)

        em.add_field(name = "**Kaul**", value =
        """
        ***!rank*** - gives you the Kaul role
        ***!derank*** - removes the Kaul role from you
        ***!kaultime [time]*** - pings everyone with the Kaul role - with the time argument, specifies when Kaul will spawn
        """)


        em.add_field(name = "**Wiki**", value =
        """
        ***!wiki [wiki page]*** - retrieves a page from the wiki
        """)



        em.set_footer(text = "Brackets indicate a place for you to put an argument (without the brackets) - ! indicates the argument is optional")

        await self.bot.send_message(ctx.message.channel, embed = em)





def setup(bot):
    bot.add_cog(Help(bot))
