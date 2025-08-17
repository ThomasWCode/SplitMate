import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("Database\\Files\\splitmate-5a08e-firebase-adminsdk-fjgzv-97c334d17e.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://splitmate-5a08e-default-rtdb.firebaseio.com'
})

offlineDbPath = "Database\\OfflineDbFiles\\offlineDb.db"
tempOfflineDbPath = "Database\\OfflineDbFiles\\tempOfflineDb.db"

currentUser = None