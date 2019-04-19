import discord
import asyncio
from discord.ext import commands
from discord.ext.commands import Bot
import time
from item import Item

import datetime


from parser import itemsFromSpreadsheet


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



bot = commands.Bot(command_prefix='!', description='Monumenta Item Index')

items = []

enchantList = {}

admins = ["177848553924722688", "140920560610836480"] # Mehaz, Vex

def verified (id) :
    return id in admins


for name, data in ref.get().items() :
    itemName = data['name'] if 'name' in data else "ERROR"
    itemURL = data['imageURL'] if 'imageURL' in data else None
    itemTags = data['tags'] if 'tags' in data else None
    items.append(Item(itemName, itemURL, itemTags))



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


@bot.command(pass_context=True)
async def removeAllTags(ctx) :
    if verified(ctx.message.author.id) :
        for item in items :
            ref.child(item.name).set({
                'name' : item.name,
                'imageURL' : item.imageURL,
                'tags' : None,
            })

    else :
        await bot.say("You don't have permission!")


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
    cap()
    alpha()

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


# THIS DOES NOT WORK RIGHT NOW, MUST MANUALLY DELETE IN DATABASE
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

    await bot.say('What is the type of tag you are searching for? (ex. Tier, Category, Enchantments, etc.)')
    tagTypeM = await bot.wait_for_message(author = ctx.message.author)
    tagType = tagTypeM.content.capitalize()

    await bot.say('What is the tag you are searching for? (ex. Protection 1, Wooden Sword, Armor, Unique, etc.)')
    tagNameM = await bot.wait_for_message(author = ctx.message.author)
    tagName = tagNameM.content.capitalize()

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



# Kaul Stuff
# TODO: Move into separate file


@bot.command(pass_context=True)
async def rank(ctx):

    author = ctx.message.author
    mention = author.mention
    server = bot.get_server('313066655494438922')
    role = discord.utils.get(server.roles, name="Kaul")
    await bot.add_roles(author, role)

    await bot.say(mention + ", you now have the role for Kaul")

@bot.command(pass_context=True)
async def derank(ctx):

    author = ctx.message.author
    mention = author.mention
    server = bot.get_server('313066655494438922')
    role = discord.utils.get(server.roles, name="Kaul")
    await bot.remove_roles(author, role)

    await bot.say(mention + ", you have removed your role for Kaul")



recentFought = datetime.datetime.now()

@bot.command(pass_context=True)
async def kaultime(ctx, *args):

    # TODO: remove this janky ass system
    global recentFought

    author = ctx.message.author.id
    server = bot.get_server('313066655494438922')
    role = discord.utils.get(server.roles, name="Kaul")
    mention = role.mention

    time = datetime.datetime.now()
    nextTime = recentFought + datetime.timedelta(minutes=5)

    if (time > nextTime) :
        if (args) :
            await bot.say(mention + " , Kaul in " + args[0] + " seconds!")
        else :
            await bot.say(mention + ", its Kaul time!")

        recentFought = time

    else :
        wait = nextTime - time
        minutes = (wait.seconds // 60) % 60
        seconds = wait.seconds % 60
        await bot.say("You must wait " + str(minutes) + " minutes and " + str(seconds) + " seconds to ping Kaul again.")


@bot.command(pass_context=True)
async def kaulnum(ctx, *args):

    server = bot.get_server('313066655494438922')
    role = discord.utils.get(server.roles, name="Kaul")

    count = 0
    for member in server.members:
        if (role in member.roles) :
            count += 1

    await bot.say(str(count) + " players have the Kaul role")


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)

@bot.command()
async def listening():
    await bot.say('Listening')

@bot.command(pass_context=True)
async def hey(ctx):
  if ctx.message.author.id == "177848553924722688" :
      await bot.say('Hey Mehaz!')
  elif ctx.message.author.id == "140920560610836480" :
      await bot.say('Hey Vex!')
  else:
      await bot.say('Imposter!')

@bot.command(pass_context=True)
async def listitemspython(ctx):
  if verified(ctx.message.author.id) :
    print(itemList)

@bot.command(pass_context=True)
async def listenchantspython(ctx):
  if verified(ctx.message.author.id) :
    print(enchantList)

@bot.command(pass_context=True)
async def itemlist(ctx):
  output = ""
  for item in items :
      if (len(item.name) + len(output) < 2000) :
          output += item.name
          output += ", "

      else :
          await bot.say(output[:-2])
          output = item.name + ", "

  await bot.say(output[:-2])


def cap () :
    for item in items :

       name = ""
       for word in item.name.split() :
           name += word.capitalize() + " "

       item.name = name.strip()


@bot.command(pass_context=True)
async def capitalize(ctx):
    if verified(ctx.message.author.id) :
        cap()


def alpha () :
    items.sort()

@bot.command(pass_context=True)
async def alphabetize(ctx):
    if verified(ctx.message.author.id) :
        alpha()

# @bot.command(pass_context=True)
# async def createKaul(ctx):
#     if verified(ctx.message.author.id) :
#         await bot.create_role(ctx.message.server, name = "Kaul", permissions = discord.Permissions.none(), colour = discord.Colour.darker_grey(), hoist = False, mentionable = True)




bot.run('NTYxMTQ0ODcxMzk0NzM4MTgx.XJ_CUw.2g2D_HzkLcZesNKz7q9TR2S0Icg')
