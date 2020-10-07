import discord
from discord.ext import commands

from discordbook import Book, Chapter


MONUMENTA_SERVER_ID = 313066655494438922


class Kaul (commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # TODO: Debug why this doesn't work with get_guild - would reduce a lot of redundancy
        # self.server = self.bot.get_guild(MONUMENTA_SERVER_ID)
        # print("SERVER GOTTEN + " + self.server)
        # self.kaul_role = discord.utils.get(self.server.roles, name="Kaul")

    @commands.command()
    async def rank(self, ctx):

        author = ctx.author
        mention = author.mention

        server = self.bot.get_guild(MONUMENTA_SERVER_ID)
        kaul_role = discord.utils.get(server.roles, name="Kaul")

        await author.add_roles(kaul_role)
        await ctx.channel.send(mention + ", you now have the role for Kaul")

    @commands.command()
    async def derank(self, ctx):

        author = ctx.author
        mention = author.mention

        server = self.bot.get_guild(MONUMENTA_SERVER_ID)
        kaul_role = discord.utils.get(server.roles, name="Kaul")

        await author.remove_roles(kaul_role)
        await ctx.channel.send(mention + ", you have removed your role for Kaul")

    @commands.command()
    async def kaultime(self, ctx, *args):

        server = self.bot.get_guild(MONUMENTA_SERVER_ID)
        kaul_role = discord.utils.get(server.roles, name="Kaul")

        mention = kaul_role.mention

        if (args) :
            await ctx.channel.send(mention + " , Kaul in " + args[0] + " seconds!")
        else :
            await ctx.channel.send(mention + ", its Kaul time!")

    @commands.command()
    async def kaulnum(self, ctx, *args):

        server = self.bot.get_guild(MONUMENTA_SERVER_ID)
        kaul_role = discord.utils.get(server.roles, name="Kaul")

        count = 0
        for member in server.members:
            if (kaul_role in member.roles) :
                count += 1

        await ctx.channel.send(str(count) + " players have the Kaul role")

    @commands.command()
    async def whohaskaul(self, ctx, *args):

        server = self.bot.get_guild(MONUMENTA_SERVER_ID)
        kaul_role = discord.utils.get(server.roles, name="Kaul")

        members_with_role = []
        for member in server.members:
            if (kaul_role in member.roles) :
                members_with_role.append('**' + member.display_name + '** (' + member.name + ')')

        chapter = Chapter('Kaul', members_with_role)
        kaul_book = Book([chapter], title = "**Kaul Roles**", description = "Members with the Kaul Role", per_page = 10)

        await kaul_book.open_book(self.bot, ctx.channel, ctx.author)


def setup(bot):
    bot.add_cog(Kaul(bot))
