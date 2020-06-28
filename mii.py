import discord
import asyncio
from discord.ext import commands
from discord.ext.commands import Bot
from datetime import datetime
import time

from item import Item

from discordbook import Book, Chapter


bot = commands.Bot(command_prefix='!', description='Monumenta Item Index')
MONUMENTA_SERVER_ID = "313066655494438922"

admins = ["140920560610836480"] # Vex

def verified (id) :
    return id in admins


from algoliasearch.search_client import SearchClient

client = SearchClient.create('YLEE8RLU7T', '2b4b8e994594989ddcd0a8752e213672')
algolia_index = client.init_index('monumenta-item-index')



items = []

# Comment this stuff out during devtime unless needed
# Firebase initialization and creation of a reference

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage

# Fetch the service account key JSON file contents
cred = credentials.Certificate('monumenta-item-index-firebase-adminsdk-2vgeu-06804b36e1.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://monumenta-item-index.firebaseio.com/',
    'storageBucket': 'monumenta-item-index.appspot.com'
})

db = firestore.client()
bucket = storage.bucket()

# As an admin, the app has access to read and write all data, regradless of Security Rules
ref = db.collection('items')
stats = db.collection('stats').document('discord')
# print(ref.get())

retrieved_items = ref.stream()

count = 0
limit = 3

print("Loading items...")
for doc in retrieved_items :
    data = doc.to_dict()
    itemName = data['name']
    # itemURL = data['imageURL'] if 'imageURL' in data else None
    # TODO: Rework this - probably a hasImage attribute in each item
    itemURL = ''
    itemBlob = bucket.get_blob('item-images/' + itemName)
    if itemBlob :
        metadata = itemBlob.metadata
        itemURL = 'https://firebasestorage.googleapis.com/v0/b/monumenta-item-index.appspot.com/o/item-images%2F' + itemName.replace(' ', '%20') + '?alt=media' + '&token=' + metadata['firebaseStorageDownloadTokens']


    itemTags = data['tags'] if 'tags' in data else None
    # print(itemTags)
    items.append(Item(itemName, itemURL, itemTags))

    count += 1

    if count % 10 == 0 :
        print("Loaded " + str(count) + "...")

    if count >= limit :
        break


    

print("Done loading!")


bot.remove_command("help")

cogs = ['cogs.kaul', 'cogs.help', 'cogs.wiki', 'cogs.stats']

for cog in cogs:
    try:
        bot.load_extension(cog)
        print("Successfully loaded " + cog)
    except Exception as e:
        print("Failed to load extension " + cog + " because " + str(e))



@bot.event
async def on_ready():
    print('Bot is listening!')
    print('Woke up at ' + datetime.now().strftime("%m/%d/%Y %H:%M:%S"))

@bot.command()
async def ping():
    await bot.say('Pong!')


@bot.command(pass_context=True)
async def item(ctx, *args):
    if not args :
        await bot.say("**No item name specified!**")
        return

    itemSearch = ' '.join(args).lower().replace("'", "")

    found = False
    for item in items :
        if (itemSearch == item.getSearchTerm()) :
            em = discord.Embed(title=item.name, description="[Edit](https://vvvvv.dev/search/" + item.name.replace(' ', '%20') + ")", color=1)

            for tagType, aTags in item.tags.items() :

                em.add_field(name = tagType, value = aTags, inline = False)

            if (item.imageURL) :
                itemImage = str(item.imageURL)
                em.set_image(url=itemImage)


            await bot.send_message(ctx.message.channel, embed = em)
            found = True
            break

    if not found :
        fail = stats.get().to_dict()['itemFail']
        stats.update({'itemFail' : fail + 1})
        await bot.say("**Item not found**")

    else :
        success = stats.get().to_dict()['itemFound']
        stats.update({'itemFound' : success + 1})



    print ('Found Item')


@bot.command(pass_context=True)
async def search(ctx, *args):

    search_results = algolia_index.search(args, {
        'attributesToRetrieve': [
            'name'
        ],
        'hitsPerPage': 20
    })

    em = discord.Embed(title="***Search Results***", color=1)
    em.description = 'Query: ' + str(args)

    display_results = ''
    for hit in search_results['hits'] :
        display_results += hit['name'] + '\n'

    em.add_field(name = 'Results', value = display_results, inline = False)

    search_number = stats.get().to_dict()['search']
    stats.update({'search' : search_number + 1})

    await bot.send_message(ctx.message.channel, embed = em)





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

    em = discord.Embed(title="***Tag Search***", description="[Website](https://vvvvv.dev/)", color=1)


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

    # Temporary solution to convert to book system
    if not taggedItems :
        taggedItems.append("\a")

    tag_chapters = { tagName : taggedItems }

    tag_book = Book(tag_chapters, title = "***Tagged Items***", description = "**" + tagType + "**", per_page = 20)
    em = tag_book.get_current_page()
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
            tag_book.one_page_backward()

        elif reacted_emoji == '\U000027a1' :
            tag_book.one_page_forward()

        elif reacted_emoji == '\U000023ea' :
            tag_book.page_backward(5)

        elif reacted_emoji == '\U000023e9' :
            tag_book.page_forward(5)


        new_embed = tag_book.get_current_page()
        await bot.edit_message(book_message, embed = new_embed)
        response = await bot.wait_for_reaction(OPTIONS, user = ctx.message.author, timeout=10.0, message = book_message)


    else :
        await bot.clear_reactions(book_message)


    tag_search_number = stats.get().to_dict()['tagSearch']
    stats.update({'tagSearch' : tag_search_number + 1})

    print ('Tag Search')


@bot.command(pass_context=True)
async def itemlist(ctx) :

    items.sort()

    item_line = 0
    chapters = []
    for i in range(65, 91) :
        chapter_lines = []
        letter_title = chr(i)

        while item_line < len(items) and items[item_line].name[0] == letter_title :
            chapter_lines.append(items[item_line].name)
            item_line += 1
        
        chapter = Chapter(title = letter_title, lines = chapter_lines)
        chapters.append(chapter)



    itemlist_number = stats.get().to_dict()['itemlist']
    stats.update({'itemlist' : itemlist_number + 1})

    item_book = Book(chapters, title = "**Item List**", description = "**Hit the reaction buttons to go forwards or backwards!**", per_page = 20)

    await item_book.open_book(bot, ctx.message.channel, ctx.message.author)
    





TOKEN = open("bot-token").read().rstrip()
bot.run(TOKEN)
