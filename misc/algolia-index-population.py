from algoliasearch.search_client import SearchClient
import json


client = SearchClient.create('YLEE8RLU7T', '2b4b8e994594989ddcd0a8752e213672')
index = client.init_index('monumenta-item-index')

with open('items-json.json') as f:
    items = json.load(f)

index.save_objects(items, {'autoGenerateObjectIDIfNotExist': True});
