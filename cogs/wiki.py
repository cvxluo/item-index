import discord
from discord.ext import commands

import wikia


class Wiki (commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # Wiki integration
    @commands.command()
    async def wiki(self, ctx, *args) :

        if not args :
            await ctx.channel.send("Please provide a wiki page to search!")
            return

        message = ' '.join(args)
        try :
            page = wikia.page("monumentammo", message)

        except :
            await ctx.channel.send("Wiki page not found!")

        else :
            output = ""
            content = page.content
            # TODO: Better formatting for wiki stuff
            #content.replace('\n', '\n\n')

            while len(content) > 1500 :
                output = content[:1500]
                content = content[1500:]
                await ctx.channel.send("```" + output + "```")

            output = content
            await ctx.channel.send("```" + output + "```")
            await ctx.channel.send("Full page at: " + page.url.replace(' ', '_'))




def setup(bot):
    bot.add_cog(Wiki(bot))
