import pymongo
url= 'mongodb+srv://root:GM22!@aws48765.5mur5ao.mongodb.net/?retryWrites=true&w=majority&appName=aws48765'
client =pymongo.MongoClient(url)

db=client['demo']