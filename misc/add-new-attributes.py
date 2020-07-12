import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore
 

# Fetch the service account key JSON file contents
cred = credentials.Certificate('monumenta-item-index-firebase-adminsdk-2vgeu-06804b36e1.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://monumenta-item-index.firebaseio.com/'
})

# As an admin, the app has access to read and write all data, regradless of Security Rules
ref = db.reference('items')
# print(ref.get())

fs = firestore.client()
fs_ref = fs.collection('items')


from algoliasearch.search_client import SearchClient


client = SearchClient.create('YLEE8RLU7T', '2b4b8e994594989ddcd0a8752e213672')
index = client.init_index('monumenta-item-index')

browse = index.browse_objects()

limit = 10
count = 0
for item_info in browse :

    fs_ref.document(item_info['name']).update({
        'objectID' : item_info['objectID']
    })

    print(item_info['name'])

    """
    count += 1
    if count >= limit :
        break
    """

