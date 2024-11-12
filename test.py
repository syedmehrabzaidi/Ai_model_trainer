# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
# # uri = "mongodb+srv://mehrab:<admin123>@clusterforme.vysik.mongodb.net/?retryWrites=true&w=majority&appName=Clusterforme"
# uri = "mongodb+srv://mehrab:admin123@clusterforme.vysik.mongodb.net/"
# # uri = "mongosh "mongodb+srv://clusterforme.vysik.mongodb.net/" --apiVersion 1 --username mehrab"
# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))
# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)



# import os
# from sendgrid import SendGridAPIClient
a = "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"

# sg = SendGridAPIClient("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")

# data = {
#     "name": "My API Key",
#     "scopes": ["mail.send", "alerts.create", "alerts.read"],
# }

# response = sg.client.api_keys.post(request_body=data)

# print(response.status_code)
# print(response.body)
# print(response.headers)

# api_key_id = "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"

# response = sg.client.api_keys._(api_key_id).get()

# print(response.status_code)
# print(response.body)
# print(response.headers)


import os
from sendgrid import SendGridAPIClient

# Ensure the environment variable is set
sendgrid_api_key = a
if not sendgrid_api_key:
    raise ValueError("SENDGRID_SECRET_KEY environment variable is not set")

sg = SendGridAPIClient(sendgrid_api_key)

data = {
    "name": "My_API",
    "scopes": ["mail.send", "alerts.create", "alerts.read"],
}

try:
    response = sg.client.api_keys.post(request_body=data)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(f"An error occurred: {e}")