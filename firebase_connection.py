import os
import firebase_admin
#from firebase_admin import credentials
from firebase_admin import firestore

import firebase_admin
from firebase_admin import credentials
#cred = credentials.Certificate("firebase-sdk.json")

cred = credentials.Certificate("firebase3-sdk.json")
firebase_admin.initialize_app(cred)

db=firestore.client()


new_data={
    "id":1,
    "name":"new Data",
    "status":"Test"
}

# db.collection('TestingData').add(new_data)
# if result:
#     for doc in result:
#         print(doc.to_dict()['amount'])
#         # print(doc.to_dict()['name'])
