# import pymongo
# from decouple import config

# # Load MongoDB URI and DB Name from .env
# MONGO_URI = config('MONGO_URI')
# MONGO_DB_NAME = config('MONGO_DB_NAME')

# # Create a MongoClient to connect to MongoDB
# client = pymongo.MongoClient(MONGO_URI)

# # Get the database
# db = client[MONGO_DB_NAME]

# # Use the database
# print(db.name)  # Should print 'dev' if the connection is successful

from pymongo import MongoClient
from datetime import datetime

import logging

# logging.basicConfig(level=logging.DEBUG)

# MongoDB URI
MONGO_DB = MongoClient("mongodb+srv://syedmehrab:admin123@cluster0.qyxmn12.mongodb.net/test?retryWrites=true&w=majority&ssl=true")
                        #mongosh "mongodb+srv://cluster0.qyxmn12.mongodb.net/" --apiVersion 1 --username syedmehrab
                        #  mongodb+srv://username:passwordddddddd@cluster0.mongodb.net/dbname?retryWrites=true&w=majority&ssl=true


db = MONGO_DB['dev']  # your database name
print("-----------------------",db)

collection = db['users1']  # Correctly accessing the 'users' collection

# Dummy data to insert
dummy_users = [
    {
        'name': 'Alice Johnson',
        'email': 'alice.johnson@example.com',
        'password': 'hashedpassword123',  # In a real app, this should be a hashed password
        'subscription': True
    },
    {
        'name': 'Bob Smith',
        'email': 'bob.smith@example.com',
        'password': 'hashedpassword456',
        'subscription': False
    },
    {
        'name': 'Charlie Brown',
        'email': 'charlie.brown@example.com',
        'password': 'hashedpassword789',
        'subscription': True
    },
    {
        'name': 'Diana Prince',
        'email': 'diana.prince@example.com',
        'password': 'hashedpassword101',
        'subscription': False
    },
    {
        'name': 'Eve Adams',
        'email': 'eve.adams@example.com',
        'password': 'hashedpassword202',
        'subscription': True
    }
]

# Insert the dummy users into the collection
result = collection.insert_many(dummy_users)

# Print the inserted IDs to confirm
print(f'Inserted {len(result.inserted_ids)} dummy users.')


# import pymongo
# from pymongo.errors import ConnectionFailure

# MONGO_URI = "mongodb+srv://admin:admin@cluster0.wmpao.mongodb.net/dev?retryWrites=true&w=majority&ssl=true&tls=true&tlsVersion=TLS1_2"

# try:
#     client = pymongo.MongoClient(MONGO_URI)
#     client.admin.command('ping')  # Test the connection
#     print("Connected successfully to MongoDB!")
# except ConnectionFailure as e:
#     print(f"Could not connect to MongoDB: {e}")
