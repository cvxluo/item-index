import discord
from discord.ext import commands


MONUMENTA_SERVER_ID = "313066655494438922"



class Kaul:
    def __init__(self, bot):
        self.bot = bot



    @commands.command(pass_context=True)
    async def rank(self, ctx):

        author = ctx.message.author
        mention = author.mention
        server = self.bot.get_server(MONUMENTA_SERVER_ID)
        role = discord.utils.get(server.roles, name="Kaul")
        await self.bot.add_roles(author, role)

        await self.bot.say(mention + ", you now have the role for Kaul")

    @commands.command(pass_context=True)
    async def derank(self, ctx):

        author = ctx.message.author
        mention = author.mention
        server = self.bot.get_server(MONUMENTA_SERVER_ID)
        role = discord.utils.get(server.roles, name="Kaul")
        await self.bot.remove_roles(author, role)

        await self.bot.say(mention + ", you have removed your role for Kaul")


    @commands.command(pass_context=True)
    async def kaultime(self, ctx, *args):

        author = ctx.message.author.id
        server = self.bot.get_server(MONUMENTA_SERVER_ID)
        role = discord.utils.get(server.roles, name="Kaul")
        mention = role.mention


        if (args) :
            await self.bot.say(mention + " , Kaul in " + args[0] + " seconds!")
        else :
            await self.bot.say(mention + ", its Kaul time!")


    @commands.command(pass_context=True)
    async def kaulnum(self, ctx, *args):

        server = self.bot.get_server(MONUMENTA_SERVER_ID)
        role = discord.utils.get(server.roles, name="Kaul")

        count = 0
        for member in server.members:
            if (role in member.roles) :
                count += 1

        await self.bot.say(str(count) + " players have the Kaul role")



    @commands.command(pass_context=True)
    async def whohaskaul(self, ctx, *args):

        server = self.bot.get_server(MONUMENTA_SERVER_ID)
        role = discord.utils.get(server.roles, name="Kaul")

        members_with_role = []
        for member in server.members:
            if (role in member.roles) :
                members_with_role.append(member)


        output = ""
        # TODO : Will break with too many members - 2000 char limit, fix later
        for member in members_with_role :
            output += "**" +member.display_name + "** (" + member.name + ")\n"

        await self.bot.say(output)






def setup(bot):
    bot.add_cog(Kaul(bot))
