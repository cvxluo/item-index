import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage


from datetime import datetime

from item import Item

import json

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
# print(ref.get())

retrieved_items = ref.stream()

items = []

print("Getting items...")
for doc in retrieved_items :
    data = doc.to_dict()
    itemName = data['name']
    # itemURL = data['imageURL'] if 'imageURL' in data else None
    # TODO: Rework this - probably a hasImage attribute in each item
    itemURL = ''
    itemBlob = bucket.get_blob('item-images/' + itemName)
    if itemBlob :
        '''
        print("PATH:", itemBlob.path)
        print("PUBLIC URL", itemBlob.public_url)
        print("MEDIA LINK", itemBlob.media_link)
        print("SELF LINK", itemBlob.self_link)
        print("METADATA", itemBlob.metadata)
        # itemURL = itemBlob.media_link + '&token=' + metadata['firebaseStorageDownloadTokens']
        '''
        metadata = itemBlob.metadata
        # TODO: Rework this as well - janky url construction
        itemURL = 'https://firebasestorage.googleapis.com/v0/b/monumenta-item-index.appspot.com/o/item-images%2F' + itemName.replace(' ', '%20') + '?alt=media' + '&token=' + metadata['firebaseStorageDownloadTokens']


    itemTags = data['tags'] if 'tags' in data else None
    # print(itemTags)
    items.append(Item(itemName, itemURL, itemTags))

print("Finished getting items!")

data = []

for item in items :

    export_item = {}
    export_item['name'] = item.name
    export_item['tags'] = item.tags

    data.append(export_item)



print(data)
now = datetime.now()
with open('backups/items-' + str(now.month) + '-' + str(now.day) + '-' + str(now.hour) + ':' + str(now.minute), 'w') as f :
    json.dump(data, f)
