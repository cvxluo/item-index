import discord
import asyncio
from discord.ext import commands
from discord.ext.commands import Bot
from datetime import datetime
import time

from item import Item

from discordbook import Book, AlphabeticalBook, Chapter


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
# limit = 30

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

    #if count >= limit :
    #    break


    

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


@bot.command()
async def item(ctx, *args):
    if not args :
        await ctx.channel.send("**No item name specified!**")
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


            print ('Found Item: ' + str(item))

            await ctx.channel.send(embed = em)
            found = True
            break

    if not found :
        fail = stats.get().to_dict()['itemFail']
        stats.update({'itemFail' : fail + 1})
        await bot.say("**Item not found**")

    else :
        success = stats.get().to_dict()['itemFound']
        stats.update({'itemFound' : success + 1})



@bot.command()
async def search(ctx, *args):

    search_results = algolia_index.search(args, {
        'attributesToRetrieve': [
            'name'
        ],
        'hitsPerPage': 20
    })

    display_results = []
    for hit in search_results['hits'] :
        display_results.append(hit['name'])

    chapter = Chapter(title = 'Results', lines = display_results)
    search_book = Book([chapter], title = "***Search Results***", description = "**Query: " + ' '.join(args) + "**", per_page = 20)

    search_number = stats.get().to_dict()['search']
    stats.update({'search' : search_number + 1})

    await search_book.open_book(bot, ctx.channel, ctx.author)




@bot.command()
async def tag(ctx):

    # 0⃣ 1⃣ 2⃣ 3⃣ 4⃣ 5⃣ 6⃣ 7⃣ 8⃣ 9⃣ 🔟 - emojis for reference

     # TODO: Include Lore?
    PRESET_TAGS = {
        "1⃣" : 'Group',
        "2⃣" : 'Tier',
        "3⃣" : 'Category',
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

    instructions_message = await ctx.channel.send(embed = em)
    for tag in PRESET_TAGS :
        await instructions_message.add_reaction(tag)



    def check_response(reaction, user) :
        return str(reaction) in PRESET_TAGS and user == ctx.author

    def check_author (message) :
        return message.author == ctx.author


    tagType = ""

    try :
        reaction, user = await bot.wait_for('reaction_add', timeout = 10.0, check = check_response)
        reaction = str(reaction)

        if reaction == "🅾" :
            await ctx.channel.send('What is the type of custom tag you are searching for? (ex. Tier, Category, Enchantments, etc.)')

            tagTypeM = await bot.wait_for('message', timeout = 10.0, check = check_author)
            tagType = tagTypeM.content.capitalize()


        else :
            for tag in PRESET_TAGS :
                if reaction == tag :
                    tagType = PRESET_TAGS[reaction]
                    await ctx.channel.send("**`You are searching in " + tagType + "!`**")


    except asyncio.TimeoutError:
        await ctx.channel.send('Timed out...')
        await instructions_message.clear_reactions()




    tag_name_message = await ctx.channel.send('What is the tag you are searching for? (ex. Protection I, Wooden Sword, Armor, Unique, etc.)')
    try :
        tagNameM = await bot.wait_for('message', timeout = 10.0, check = check_author)
        tagName = tagNameM.content.capitalize()


    except asyncio.TimeoutError:
        await ctx.channel.send('Timed out...')
        await tag_name_message.clear_reactions()
    


    # TODO : Group items into tag categories so searching is less expensive

    taggedItems = []
    for item in items :
        if tagType in item.tags.keys() and tagName in item.tags[tagType] :
            taggedItems.append(item.name)

    if not taggedItems : # If no items of the tag were found, add filler
        taggedItems.append("No items found!")

    chapter = Chapter(title = tagName, lines = taggedItems)

    tag_book = Book([chapter], title = "***Tagged Items***", description = "**" + tagType + "**", per_page = 20)

    tag_search_number = stats.get().to_dict()['tagSearch']
    stats.update({'tagSearch' : tag_search_number + 1})

    print ('Tag Search for ' + tagName + " in " + tagType)

    await tag_book.open_book(bot, ctx.channel, ctx.author)




@bot.command(pass_context=True)
async def itemlist(ctx) :

    items.sort()

    itemlist_number = stats.get().to_dict()['itemlist']
    stats.update({'itemlist' : itemlist_number + 1})

    item_book = AlphabeticalBook(items, title = "**Item List**", description = "**Hit the reaction buttons to go forwards or backwards!**", per_page = 20)

    await item_book.open_book(bot, ctx.message.channel, ctx.message.author)
    




TOKEN = open("bot-token").read().rstrip()
bot.run(TOKEN)
