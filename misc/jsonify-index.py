import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from item import Item

import json

# Fetch the service account key JSON file contents
cred = credentials.Certificate('monumenta-item-index-firebase-adminsdk-2vgeu-06804b36e1.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://monumenta-item-index.firebaseio.com/'
})

# As an admin, the app has access to read and write all data, regradless of Security Rules
ref = db.reference('items')
# print(ref.get())



items = []

for name, data in ref.get().items() :
    itemName = data['name'] if 'name' in data else "ERROR"
    itemURL = data['imageURL'] if 'imageURL' in data else None
    itemTags = data['tags'] if 'tags' in data else None
    items.append(Item(itemName, itemURL, itemTags))


data = []

for item in items :

    export_item = {}
    export_item['name'] = item.name
    export_tags = {}

    for tag in item.tags :

        conc_tag = ""
        for section in item.tags[tag] :
            conc_tag += section + '\n'


        export_tags[tag] = conc_tag

    export_item['tags'] = export_tags
    data.append(export_item)



print(data)
with open('items-json.json', 'w') as f :
    json.dump(data, f)
