import discord
import asyncio
from discord.ext import commands
from discord.ext.commands import Bot
import time


bot = commands.Bot(command_prefix='!', description='Monumenta Item Index')
itemList = {}
enchantList = {}

with open ("backup_itemList.txt", "r") as f:
  key = None
  for i, line in enumerate(f):
    if i % 2 == 0:
      key = line.strip()
    else:
      itemList[key] = line.strip()

with open ("backup_enchantList.txt", "r") as f:
  key = None
  for i, line in enumerate(f):
    if i % 2 == 0:
      key = line.strip()
    else:
      enchantList[key] = line.strip()
        
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)

@bot.command()    
async def listening():
    await bot.say('Listening')

@bot.command(pass_context=True)
async def additem(ctx):
  await bot.say('Type the name of the item you wish to add...')
  itemWait = await bot.wait_for_message(author = ctx.message.author)   
  tempItemName1 = itemWait.content.lower()
  await bot.say('Paste the link of or upload the photo you wish to add...')
  itemWaitPhoto = await bot.wait_for_message(author = ctx.message.author)
  for attachment in itemWaitPhoto.attachments:
      tempPhoto = attachment.get("url")
  tempItemPhoto1 = itemWaitPhoto.content or tempPhoto 
  itemList[tempItemName1] = tempItemPhoto1
  await bot.say('Added Item')
  print ('Added Item')

@bot.command(pass_context=True)
async def addenchant(ctx):
  await bot.say('Type the name of the enchantment you wish to add...')
  enchantWait = await bot.wait_for_message(author = ctx.message.author)   
  tempEName = enchantWait.content.lower()
  await bot.say('Paste the link of or upload the photo you wish to add...')
  enchantWaitPhoto = await bot.wait_for_message(author = ctx.message.author)
  for attachment in enchantWaitPhoto.attachments:
      EtempPhoto = attachment.get("url")
  tempEPhoto = enchantWaitPhoto.content or EtempPhoto 
  enchantList[tempEName] = tempEPhoto
  await bot.say('Added Enchantment')
  print ('Added Enchantment')

@bot.command(pass_context=True)
async def item(ctx, *args):
  g = ' '.join(args)
  f = g.lower()
  em = discord.Embed(title=f , description="Here's your item!", color=1)
  print(itemList.get(f))
  itemImage = str(itemList.get(f))
  em.set_image(url=itemImage)
  await bot.send_message(ctx.message.channel, embed = em)
  print ('Found Item')

@bot.command(pass_context=True)
async def enchant(ctx, *args):
  ge = ' '.join(args)
  fe = ge.lower()
  eme = discord.Embed(title=fe , description="Here's your enchant!", color=1)
  print(enchantList.get(fe))
  enchantImage = str(enchantList.get(fe))
  eme.set_image(url=enchantImage)
  await bot.send_message(ctx.message.channel, embed = eme)
  print ('Found Enchant')

@bot.command(pass_context=True)
async def delenchant(ctx):
  if ctx.message.author.id == "177848553924722688":
    await bot.say('Type the name of the enchant you wish to delete...')
    enchantWait = await bot.wait_for_message(author = ctx.message.author)   
    tempEDelete = enchantWait.content.lower()
    del enchantList[tempEDelete]
    await bot.say('Enchant Deleted!')
    print('Deleted Enchant')
                     
@bot.command(pass_context=True)
async def delitem(ctx):
  if ctx.message.author.id == "177848553924722688":
    await bot.say('Type the name of the item you wish to delete...')
    itemWait = await bot.wait_for_message(author = ctx.message.author)   
    tempItemDelete = itemWait.content.lower()
    del itemList[tempItemDelete]
    await bot.say('Item Deleted!')
    print('Deleted Item')
    
@bot.command(pass_context=True)
async def backup(ctx):
   if ctx.message.author.id == "177848553924722688":
    itemListItem = list(itemList.keys())
    itemListPhoto = list(itemList.values())
    with open('backup_ItemList' + '.txt', 'w') as out_file:
        for i in range(len(itemListItem)):
            out_string = ""
            out_string += str(itemListItem[i])
            out_string += "\n" + str(itemListPhoto[i])
            out_string += "\n"
            out_file.write(out_string)
    await bot.say('Backed up items!')
    print ('Backed up items')
   else:
      await bot.say("You don't have permission to do that.")

@bot.command(pass_context=True)
async def enchantbackup(ctx):
   if ctx.message.author.id == "177848553924722688":
    enchantListItem = list(enchantList.keys())
    enchantListPhoto = list(enchantList.values())
    with open('backup_enchantList' + '.txt', 'w') as eout_file:
        for ei in range(len(enchantListItem)):
            eout_string = ""
            eout_string += str(enchantListItem[ei])
            eout_string += "\n" + str(enchantListPhoto[ei])
            eout_string += "\n"
            eout_file.write(eout_string)
    await bot.say('Backed up enchants!')
    print ('Backed up')
   else:
      await bot.say("You don't have permission to do that.")


@bot.command(pass_context=True)
async def hey(ctx):
  if ctx.message.author.id == "177848553924722688":
      await bot.say('Hey Mehaz!')
  else:
      await bot.say('Imposter!')

@bot.command(pass_context=True)
async def listitemspython(ctx):
  if ctx.message.author.id == "177848553924722688":
    print(itemList)

@bot.command(pass_context=True)
async def listenchantspython(ctx):
  if ctx.message.author.id == "177848553924722688":
    print(enchantList)

@bot.command()
async def itemlist():
  itemsinList = itemList.keys()
  itemsList = ', '.join(itemsinList)
  if len(itemsList) > 2000:
    itemsList2 = itemsList[:2000]
    itemsList3 = itemsList[2000:4000]
    itemsList4 = itemsList[4000:6000]
    await bot.say(itemsList2)
    await bot.say(itemsList3)
    await bot.say(itemsList4)
  else:
    await bot.say(itemsList)
     
@bot.command()
async def enchantlist():
  EinList = enchantList.keys()
  EList = ', '.join(EinList)
  await bot.say(EList)
     
bot.run('NTYxMTQ0ODcxMzk0NzM4MTgx.XJ_CUw.2g2D_HzkLcZesNKz7q9TR2S0Icg')


