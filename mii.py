import discord
import asyncio
from discord.ext import commands
from discord.ext.commands import Bot
import time

from item import Item
from Book import Book

import datetime


from parser import itemsFromSpreadsheet
import wikia


bot = commands.Bot(command_prefix='!', description='Monumenta Item Index')
MONUMENTA_SERVER_ID = "313066655494438922"

items = []

admins = ["177848553924722688", "140920560610836480"] # Mehaz, Vex

def verified (id) :
    return id in admins



# Comment this stuff out during devtime unless needed
# Firebase initialization and creation of a reference

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Fetch the service account key JSON file contents
cred = credentials.Certificate('monumenta-item-index-firebase-adminsdk-2vgeu-06804b36e1.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://monumenta-item-index.firebaseio.com/'
})

# As an admin, the app has access to read and write all data, regradless of Security Rules
ref = db.reference('items')
# print(ref.get())


for name, data in ref.get().items() :
    itemName = data['name'] if 'name' in data else "ERROR"
    itemURL = data['imageURL'] if 'imageURL' in data else None
    itemTags = data['tags'] if 'tags' in data else None
    items.append(Item(itemName, itemURL, itemTags))
#



cogs = ['cogs.kaul']

if __name__ == '__main__':
    for cog in cogs:
        try:
            bot.load_extension(cog)
            print("Successfully loaded " + cog)
        except Exception as e:
            print("Failed to load extension " + cog)



@bot.event
async def on_ready():
    print('Bot is listening')

@bot.command()
async def ping():
    await bot.say('Pong!')



bot.remove_command("help")
@bot.command(pass_context=True)
async def help(ctx, *args) :

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

    em.set_footer(text = "Brackets indicate a place for you to put an input (without the brackets)")

    await bot.send_message(ctx.message.channel, embed = em)



# Wiki integration
@bot.command(pass_context=True)
async def wiki(ctx, *args) :
    message = ' '.join(args)
    try :
        page = wikia.page("monumentammo", message)

    except :
        await bot.say("Wiki page not found!")

    else :
        output = ""
        content = page.content
        # TODO: Better formatting for wiki stuff
        #content.replace('\n', '\n\n')

        while len(content) > 1500 :
            output = content[:1500]
            content = content[1500:]
            await bot.say("```" + output + "```")

        output = content
        await bot.say("```" + output + "```")
        await bot.say("Full page at: " + page.url.replace(' ', '_'))




@bot.command(pass_context=True)
async def getFromSpreadsheet(ctx) :
    if not verified(ctx.message.author.id) :
        return

    await bot.say("Attempting to get items from spreadsheet")

    spreadsheet = itemsFromSpreadsheet()
    tagNames = spreadsheet.pop(0)
    tagNames.pop(4)

    for item in spreadsheet :
        name = item.pop(4).strip()
        # TODO: Fix this garbage
        # Question marks aren't allowed, but there really should be a better way to sanitize strings before storage
        name = name.replace('.', '')
        print(name)
        name = name.split('\n')[0]
        if ('(' in name) :
            name = name[:(name.find('(') - 1)]
            name.strip()
        tags = {}

        for i in range(len(item)) :
            if (item[i]) :
                # TODO:  this is horrific pls make clear
                tags[tagNames[i]] = item[i].split('\n') #.replace(':', ':\n').replace(',', ',\n') #

        ref.child(name).update({
            'name' : name,
            'tags' : tags,
        })
        #await bot.say(str(item))
    await bot.say("Successfully updated from spreadsheet")


# Obsolete, Firebase updates should happen automatically
@bot.command(pass_context=True)
async def backup(ctx):
    if verified(ctx.message.author.id) :

        for item in items :
            ref.child(item.name).set({
                'name' : item.name,
                'imageURL' : item.imageURL,
                'tags' : item.tags
            })

        await bot.say('Backed up items to Firebase')
        print ('Backed up items')
    else:
      await bot.say("You don't have permission to do that.")


@bot.command(pass_context=True)
async def additem(ctx):
    await bot.say('What is the item NAME?')
    itemWait = await bot.wait_for_message(author = ctx.message.author)
    itemName = itemWait.content

    await bot.say("What is the IMAGE for the item? (If you don't have an image, type 'none')")
    itemWaitPhoto = await bot.wait_for_message(author = ctx.message.author)
    itemPhoto = ""
    if (itemWaitPhoto.content != 'none' or itemWaitPhoto.attachments) :
        for attachment in itemWaitPhoto.attachments:
            tempPhoto = attachment.get("url")

        itemPhoto = itemWaitPhoto.content or tempPhoto


    # TODO: This logic is super convoluted for a simple task, please fix

    tags = {}
    await bot.say("Does this item have tags? (If you don't have any tags, or if you're done, type 'done')")
    tagMessage = await bot.wait_for_message(author = ctx.message.author)
    if (tagMessage.content != 'done') :
        await bot.say("What is the type of tag you want to add? (ex. Enchantments, Location, etc.)")
        tagType = await bot.wait_for_message(author = ctx.message.author)
        await bot.say("What is the tag you would like to add? (ex. Protection 2, Halls of Wind and Blood)")
        tagName = await bot.wait_for_message(author = ctx.message.author)

        while (tagName.content != 'done') :
            tags[tagType.content] = tagName.message.content
            await bot.say("If you have additional tags, please enter them one at a time. Otherwise, type 'done'.")
            tagName = await bot.wait_for_message(author = ctx.message.author)

        await bot.say("Does this item have more tags? (If you don't have any more tags, or if you're done, type 'done')")
        tagMessage = await bot.wait_for_message(author = ctx.message.author)


    item = Item(itemName, itemPhoto, tags)
    items.append(item)

    ref.child(itemName).set({
        'name' : itemName,
        'imageURL' : itemPhoto,
        'tags' : tags
    })


    await bot.say('Added Item ' + itemWait.content)
    print ('Added Item')


@bot.command(pass_context=True)
async def addtag(ctx):
    await bot.say('What item would you like to tag?')
    toTag = await bot.wait_for_message(author = ctx.message.author)
    itemSearch = toTag.content.lower().replace("'", "")


    await bot.say('What is the type of tag you are adding?')
    tagType = await bot.wait_for_message(author = ctx.message.author)

    await bot.say('What tag would you like to add?')
    tag = await bot.wait_for_message(author = ctx.message.author)

    capWords = []
    for word in tag.content.split() :
        capWords.append(word.capitalize())

    for item in items :
        if (itemSearch == item.getSearchTerm()) :
            item.addTag(tagType.content.capitalize(), ' '.join(capWords))
            ref.child(item.name).update({
                'tags' : item.tags
            })
            break


    await bot.say('Added ' + tag.content + ' to ' + toTag.content)
    print ('Added Tag')



@bot.command(pass_context=True)
async def item(ctx, *args):
  itemSearch = ' '.join(args).lower().replace("'", "")

  found = False
  for item in items :
      if (itemSearch == item.getSearchTerm()) :
          em = discord.Embed(title=item.name, color=1)

          for tagType, aTags in item.tags.items() :

              tag = ', '.join(aTags)
              em.add_field(name = tagType, value = tag, inline = False)

          if (item.imageURL) :
              itemImage = str(item.imageURL)
              em.set_image(url=itemImage)

          await bot.send_message(ctx.message.channel, embed = em)
          found = True
          break

  if not found :
      await bot.say("Item not found")


  print ('Found Item')


@bot.command(pass_context=True)
async def delitem(ctx):
  if verified(ctx.message.author.id):
    await bot.say('What item would you like to delete?')
    itemWait = await bot.wait_for_message(author = ctx.message.author)
    itemSearch = itemWait.content.lower().replace("'", "")

    for i in range(len(items)) :
        if (itemSearch == items[i].getSearchTerm()) :
            del items[i]
            ref.child(items[i].name).delete()
            break

    await bot.say('Item Deleted!')
    print('Deleted Item')


@bot.command(pass_context=True)
async def deltag(ctx, *args):
    await bot.say('Type the name of the item...')
    itemWait = await bot.wait_for_message(author = ctx.message.author)
    itemSearch = itemWait.content.lower().replace("'", "")

    await bot.say('Type the type of tag...')
    tagType = await bot.wait_for_message(author = ctx.message.author)

    await bot.say('Type the tag name...')
    tagName = await bot.wait_for_message(author = ctx.message.author)

    for item in items :
        if (itemSearch == item.getSearchTerm()) :
            item.deleteTag(tagType.content, tagName.content)
            ref.child(item.name).update({
                'tags' : item.tags
            })
            break

    await bot.say('Tag Deleted!')

    print('Deleted Item')


@bot.command(pass_context=True)
async def tag(ctx):

    # 0⃣ 1⃣ 2⃣ 3⃣ 4⃣ 5⃣ 6⃣ 7⃣ 8⃣ 9⃣ 🔟 - emojis for reference

     # TODO: Include Lore?
    PRESET_TAGS = {
    "1⃣" : 'Group',
    "2⃣" : 'Tier',
    "3⃣" :'Category',
    "4⃣" : 'Type of Item',
    "5⃣" : 'Equip Slot',
    "6⃣" : 'Enchantments',
    "7⃣" : 'Bonus Effects',
    "8⃣" : 'Where to Obtain',
    "🅾" : 'Other'
    }

    em = discord.Embed(title="***Tag Search***", color=1)


    instructions = ""

    for tag in PRESET_TAGS :
        instructions += tag + " - " + PRESET_TAGS[tag] + "\n"

    em.add_field(name = "React with the tag you would like to search for!", value = instructions, inline = False)
    em.set_footer(text = "If you are searching for a tag not listed, react with the O")

    instructions_message = await bot.send_message(ctx.message.channel, embed = em)
    for tag in PRESET_TAGS :
        await bot.add_reaction(instructions_message, tag)

    response = await bot.wait_for_reaction(PRESET_TAGS.keys(), user = ctx.message.author, timeout=10.0, message = instructions_message)

    tagType = ""

    if response : # If timeout, response will be None
        reacted_emoji = response.reaction.emoji

        if reacted_emoji == "🅾" :
            await bot.say('What is the type of custom tag you are searching for? (ex. Tier, Category, Enchantments, etc.)')
            tagTypeM = await bot.wait_for_message(author = ctx.message.author)
            tagType = tagTypeM.content.capitalize()

        else :
            for tag in PRESET_TAGS :
                if reacted_emoji == tag :
                    tagType = PRESET_TAGS[reacted_emoji]
                    await bot.say("**`You are searching in " + tagType + "!`**")

    else :
        await bot.say("**`Timed out...`**")
        return



    await bot.say('What is the tag you are searching for? (ex. Protection I, Wooden Sword, Armor, Unique, etc.)')
    tagNameM = await bot.wait_for_message(author = ctx.message.author)
    tagName = tagNameM.content.capitalize()


    # TODO : Group items into tag categories so searching is less expensive

    taggedItems = []
    for item in items :
        if tagType in item.tags.keys() and tagName in item.tags[tagType] :
            taggedItems.append(item.name)

    output = ""
    if len(taggedItems) > 0 :
        output += "Items with " + tagName + ":\n"
        for itemName in taggedItems :
            output += itemName + "\n"

    else :
        output += "No items found with that tag"

    await bot.say(output)

    print ('Tag Search')


@bot.command(pass_context=True)
async def itemlist(ctx) :

    items.sort()
    chapters = {}
    for i in range(65, 91) :
        chapters[chr(i)] = []
    chapters['c'] = []

    for item in items :
        chapters[item.name[0]].append(item)

    item_book = Book(chapters, title = "**Item List**", description = "**Hit the reaction buttons to go forwards or backwards!**", per_page = 20)
    em = item_book.get_current_page()
    book_message = await bot.send_message(ctx.message.channel, embed = em)

    OPTIONS = [
        '\U000023ea', # Reverse
        '\U00002b05', # Left Arrow
        '\U000027a1', # Right Arrow
        '\U000023e9', # Fast Forward
    ]

    for option in OPTIONS :
        await bot.add_reaction(book_message, option)


    response = await bot.wait_for_reaction(OPTIONS, user = ctx.message.author, timeout=10.0, message = book_message)

    while response :
        reacted_emoji = response.reaction.emoji

        if reacted_emoji == '\U00002b05' :
            item_book.one_page_backward()

        elif reacted_emoji == '\U000027a1' :
            item_book.one_page_forward()

        elif reacted_emoji == '\U000023ea' :
            item_book.page_backward(5)

        elif reacted_emoji == '\U000023e9' :
            item_book.page_forward(5)


        new_embed = item_book.get_current_page()
        await bot.edit_message(book_message, embed = new_embed)
        response = await bot.wait_for_reaction(OPTIONS, user = ctx.message.author, timeout=10.0, message = book_message)


    else :
        await bot.clear_reactions(book_message)

# @bot.command(pass_context=True)
# async def createKaul(ctx):
#     if verified(ctx.message.author.id) :
#         await bot.create_role(ctx.message.server, name = "Kaul", permissions = discord.Permissions.none(), colour = discord.Colour.darker_grey(), hoist = False, mentionable = True)



TOKEN = open("bot-token").read().rstrip()
bot.run(TOKEN)
