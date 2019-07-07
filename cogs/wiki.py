import discord
from discord.ext import commands

import wikia


class Wiki:
    def __init__(self, bot):
        self.bot = bot


    # Wiki integration
    @commands.command(pass_context=True)
    async def wiki(self, ctx, *args) :

        if not args :
            await self.bot.say("Please provide a wiki page to search!")
            return

        message = ' '.join(args)
        try :
            page = wikia.page("monumentammo", message)

        except :
            await self.bot.say("Wiki page not found!")

        else :
            output = ""
            content = page.content
            # TODO: Better formatting for wiki stuff
            #content.replace('\n', '\n\n')

            while len(content) > 1500 :
                output = content[:1500]
                content = content[1500:]
                await self.bot.say("```" + output + "```")

            output = content
            await self.bot.say("```" + output + "```")
            await self.bot.say("Full page at: " + page.url.replace(' ', '_'))





def setup(bot):
    bot.add_cog(Wiki(bot))
