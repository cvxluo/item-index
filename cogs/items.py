import discord
from discord.ext import commands
import os

# Firebase and GCP tools
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage

from google.cloud import secretmanager

# Algolia
from algoliasearch.search_client import SearchClient


from discordbook import Book, Chapter, AlphabeticalBook


class Items (commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # Firebase initialization and creation of a reference
        CREDENTIAL_PATH = 'monumenta-item-index-firebase-adminsdk-vm0ae-0bfa3c4c42.json'
        algolia_api_key = ""
        secret_manager = None

        # If dev credentials are present, bot should be run on development mode, and initialized with those dev credentials
        if os.path.exists(CREDENTIAL_PATH) :
            # Fetch the service account key JSON file contents
            cred = credentials.Certificate(CREDENTIAL_PATH)

            # Initialize the app with a service account, granting admin privileges
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://monumenta-item-index.firebaseio.com/',
                'storageBucket': 'monumenta-item-index.appspot.com'
            })

            # Create the Secret Manager client.
            secret_manager = secretmanager.SecretManagerServiceClient.from_service_account_json(CREDENTIAL_PATH)


        # Otherwise, try to initialize from default parameters, assuming running on Compute Engine
        else :
            firebase_admin.initialize_app(options = {
                'storageBucket': 'monumenta-item-index.appspot.com'
            })

            # Create the Secret Manager client.
            secret_manager = secretmanager.SecretManagerServiceClient()


        db = firestore.client()
        bucket = storage.bucket()

        # As an admin, the app has access to read and write all data, regradless of Security Rules
        ref = db.collection('items')
        stats = db.collection('stats').document('discord')
        # print(ref.get())

        self.item_ref = ref
        self.stats_ref = stats
        self.storage_bucket = bucket



        # Set up the Algolia Client

        # Build the resource name of the secret version.
        algolia_secret_path = secret_manager.secret_version_path('monumenta-item-index', 'algolia-api-key', 'latest')

        # Access the secret version.
        response = secret_manager.access_secret_version(algolia_secret_path)

        payload = response.payload.data.decode('UTF-8')
        algolia_api_key = payload


        client = SearchClient.create('YLEE8RLU7T', algolia_api_key)
        self.algolia_index = client.init_index('monumenta-item-index')


    @commands.command()
    async def item(self, ctx, *args) :
        
        # No argument provided
        if not args :
            failure_embed = discord.Embed(title="No item name specified!", color=15158332)

            await ctx.channel.send(embed=failure_embed)
            return


        item_name = " ".join([word.capitalize() for word in args])
        item_data = self.item_ref.document(item_name).get().to_dict()

        # If not found - item_data is None
        if not item_data :

            fail = self.stats_ref.get().to_dict()['itemFail']
            self.stats_ref.update({'itemFail' : fail + 1})

            # Perform search - if only one result, ask user if it is correct
            search_results = self.algolia_index.search(args, {
                'attributesToRetrieve': [
                    'name'
                ],
                'hitsPerPage': 5
            })

            if len(search_results['hits']) :
                possible_item_name = search_results['hits'][0]['name']

                confirm_embed = discord.Embed(title = "Item not found!", description="Did you mean **" + possible_item_name + "**?")
                possible_question = await ctx.channel.send(embed=confirm_embed)
                await possible_question.add_reaction('\U00002705')

                def check_response(reaction, user) :
                    return str(reaction) == '\U00002705' and user == ctx.author

                reaction, user = await self.bot.wait_for('reaction_add', timeout = 10.0, check = check_response)
                reaction = str(reaction)

                if (reaction == '\U00002705') :

                    item_name = possible_item_name
                    item_data = self.item_ref.document(possible_item_name).get().to_dict()


            else :
                failure_embed = discord.Embed(title="Item not found!", description="This item may not be in the database - you can [add it here](https://vvvvv.dev/add)", color=15158332)

                await ctx.channel.send(embed=failure_embed)
                return


        item_embed = discord.Embed(title=item_name, description="[Edit](https://vvvvv.dev/search/" + item_name.replace(' ', '%20') + ")", color=1)
        if 'tags' in item_data :
            for tag_name, tag_content in item_data['tags'].items() :
                item_embed.add_field(name = tag_name, value = tag_content, inline = False)

        blob = self.storage_bucket.get_blob('item-images/' + item_name)
        if blob :
            metadata = blob.metadata
            image_URL = 'https://firebasestorage.googleapis.com/v0/b/monumenta-item-index.appspot.com/o/item-images%2F' + item_name.replace(' ', '%20') + '?alt=media' + '&token=' + metadata['firebaseStorageDownloadTokens']

            item_embed.set_image(url=image_URL)
        
        await ctx.channel.send(embed = item_embed)

        success = self.stats_ref.get().to_dict()['itemFound']
        self.stats_ref.update({'itemFound' : success + 1})



    @commands.command()
    async def search(self, ctx, *args):

        search_results = self.algolia_index.search(args, {
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

        search_number = self.stats_ref.get().to_dict()['search']
        self.stats_ref.update({'search' : search_number + 1})

        await search_book.open_book(self.bot, ctx.channel, ctx.author)



def setup(bot):
    bot.add_cog(Items(bot))