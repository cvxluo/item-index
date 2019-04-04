import discord
import asyncio
from discord.ext import commands
from discord.ext.commands import Bot
import time
from item import Item



bot = commands.Bot(command_prefix='!', description='Monumenta Item Index')

items = []

enchantList = {}

admins = ["177848553924722688", "140920560610836480"] # Mehaz, Vex

def verified (id) :
    return id in admins



with open ("items.txt", "r") as f:

  for line in f :
      data = line.split()
      name = " ".join(data[0].split("$"))

      tags = {}
      if (len(data) > 2) :
          tagData = data[2].split("|")
          for tag in tagData :
              nameSplit = tag.split(":")
              tagName = nameSplit[0]

              t = nameSplit[1].split(',')

              tags[tagName] = []
              for attribute in t :
                  tags[tagName].append(attribute.replace('$', ' '))


      item = Item(name, data[1], tags)
      items.append(item)


@bot.command(pass_context=True)
async def backup(ctx):
   if verified(ctx.message.author.id) :
    with open('items.txt', 'w') as out_file:
        for item in items :
            data = ""

            data = "$".join(item.name.split()) + " "

            data += item.imageURL + " "

            t = []
            for tagType, aTags in item.tags.items() :
                newTag = ""
                newTag += tagType + ":"

                storeTags = []
                for tag in aTags :
                    storeTags.append(tag.replace(' ', '$'))

                newTag += ','.join(storeTags)

                t.append(newTag)

            data += '|'.join(t)

            data += "\n"

            out_file.write(data)


    await bot.say('Backed up items!')
    print ('Backed up items')
   else:
      await bot.say("You don't have permission to do that.")


@bot.command(pass_context=True)
async def additem(ctx):
  await bot.say('Type the name of the item you wish to add...')
  itemWait = await bot.wait_for_message(author = ctx.message.author)
  itemName = itemWait.content.lower()
  await bot.say('Paste the link of or upload the photo you wish to add...')
  itemWaitPhoto = await bot.wait_for_message(author = ctx.message.author)
  for attachment in itemWaitPhoto.attachments:
      tempPhoto = attachment.get("url")
  itemPhoto = itemWaitPhoto.content or tempPhoto

  item = Item(itemName, itemPhoto)
  items.append(item)
  await bot.say('Added Item ' + itemWait.content)
  print ('Added Item')


@bot.command(pass_context=True)
async def addtag(ctx):
    if not verified(ctx.message.author.id) :
        return
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
    await bot.say('Type the name of the item you wish to delete...')
    itemWait = await bot.wait_for_message(author = ctx.message.author)
    itemSearch = itemWait.content.lower().replace("'", "")

    for i in range(len(items)) :
        if (itemSearch == items[i].getSearchTerm()) :
            del items[i]
            break

    await bot.say('Item Deleted!')
    print('Deleted Item')


@bot.command(pass_context=True)
async def deltag(ctx, *args):
    if verified(ctx.message.author.id):
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
                break

        await bot.say('Tag Deleted!')

        print('Deleted Item')



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

@bot.command()
async def itemlist():
  output = ""
  for item in items :
      if (len(item.name) + len(output) < 2000) :
          output += item.name
          output += ", "

      else :
          await bot.say(output[:-2])
          output = item.name + ", "

  await bot.say(output[:-2])


@bot.command(pass_context=True)
async def capitalize(ctx):
    if verified(ctx.message.author.id) :
        for item in items :

           name = ""
           for word in item.name.split() :
               name += word.capitalize() + " "

           item.name = name.strip()


@bot.command(pass_context=True)
async def alphabetize(ctx):
    if verified(ctx.message.author.id) :
        items.sort()




bot.run('NTYxMTQ0ODcxMzk0NzM4MTgx.XJ_CUw.2g2D_HzkLcZesNKz7q9TR2S0Icg')


#TRANSFER COMMAND
# with open ("backup_itemList.txt", "r") as f:
#   key = None
#   for i, line in enumerate(f):
#     if i % 2 == 0:
#       key = line.strip()
#     else:
#       itemList[key] = line.strip()
#
#
# @bot.command(pass_context=True)
# async def transfer(ctx):
#
#     with open('items.txt', 'w') as out_file:
#         for item in itemList :
#             data = ""
#             data += item + " "
#             data += itemList[item] + " "
#             data += "\n"
#
#             out_file.write(data)

#OLD READFILE (ENCHANT)
# with open ("backup_enchantList.txt", "r") as f:
#   key = None
#   for i, line in enumerate(f):
#     if i % 2 == 0:
#       key = line.strip()
#     else:
#       enchantList[key] = line.strip()


#OLD ADDITEM (ENCHANT)
# @bot.command(pass_context=True)
# async def addenchant(ctx):
#   await bot.say('Type the name of the enchantment you wish to add...')
#   enchantWait = await bot.wait_for_message(author = ctx.message.author)
#   tempEName = enchantWait.content.lower()
#   await bot.say('Paste the link of or upload the photo you wish to add...')
#   enchantWaitPhoto = await bot.wait_for_message(author = ctx.message.author)
#   for attachment in enchantWaitPhoto.attachments:
#       EtempPhoto = attachment.get("url")
#   tempEPhoto = enchantWaitPhoto.content or EtempPhoto
#   enchantList[tempEName] = tempEPhoto
#   await bot.say('Added Enchantment')
#   print ('Added Enchantment')

#OLD ITEM (ENCHANT)
# @bot.command(pass_context=True)
# async def enchant(ctx, *args):
#   ge = ' '.join(args)
#   fe = ge.lower()
#   eme = discord.Embed(title=fe , description="Here's your enchant!", color=1)
#   print(enchantList.get(fe))
#   enchantImage = str(enchantList.get(fe))
#   eme.set_image(url=enchantImage)
#   await bot.send_message(ctx.message.channel, embed = eme)
#   print ('Found Enchant')

#OLD DELITEM (ENCHANT)
# @bot.command(pass_context=True)
# async def delenchant(ctx):
#   if ctx.message.author.id == "177848553924722688":
#     await bot.say('Type the name of the enchant you wish to delete...')
#     enchantWait = await bot.wait_for_message(author = ctx.message.author)
#     tempEDelete = enchantWait.content.lower()
#     del enchantList[tempEDelete]
#     await bot.say('Enchant Deleted!')
#     print('Deleted Enchant')

#OLD BACKUP (ENCHANT)
# @bot.command(pass_context=True)
# async def enchantbackup(ctx):
#    if ctx.message.author.id == "177848553924722688":
#     enchantListItem = list(enchantList.keys())
#     enchantListPhoto = list(enchantList.values())
#     with open('backup_enchantList.txt', 'w') as eout_file:
#         for ei in range(len(enchantListItem)):
#             eout_string = ""
#             eout_string += str(enchantListItem[ei])
#             eout_string += "\n" + str(enchantListPhoto[ei])
#             eout_string += "\n"
#             eout_file.write(eout_string)
#     await bot.say('Backed up enchants!')
#     print ('Backed up')
#    else:
#       await bot.say("You don't have permission to do that.")

#OLD ENCHANT ITEM
# @bot.command()
# async def enchantlist():
#   EinList = enchantList.keys()
#   EList = ', '.join(EinList)
#   await bot.say(EList)
