# # chat/client.py

# import asyncio
# import websockets
# import json

# async def send_message():
#     uri = "ws://localhost:8000/ws/chat/lobby/"
#     async with websockets.connect(uri) as websocket:
#         while True:
#             message = input("Enter message: ")
#             await websocket.send(json.dumps({'message-----': message}))
#             try:
#                 response = await websocket.recv()
#                 print(f"Received---: {response}")
#             except websockets.exceptions.ConnectionClosedError:
#                 print("Connection closed by server")
#                 break

# asyncio.get_event_loop().run_until_complete(send_message())

# chat/client.py
# chat/client.py

import asyncio
import websockets
import json

async def send_message(token):
    uri = f"ws://localhost:8000/ws/chat/lobby/?token={token}"
    async with websockets.connect(uri) as websocket:
        while True:
            message = input("Enter message: ")
            await websocket.send(json.dumps({'message': message}))
            try:
                response = await websocket.recv()
                data = json.loads(response)
                print(f"Received from {data['user_name']} ({'Admin' if data['is_admin'] else 'User'}): {data['message']}")
            except websockets.exceptions.ConnectionClosedError:
                print("Connection closed by server")
                break


# Replace with your actual JWT token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoyMDkyNDYwMjcyLCJpYXQiOjE3MzI0NjM4NzIsImp0aSI6IjgwYmNjYzRhYTBjNjQwZmY5MjBhMTYzMWU1MWI4OTU3IiwidXNlcl9pZCI6IjY3NDBhMGFkMzc5YzI3OGYwMGU3ZTliMSJ9.v7H1doaQc-VfhB26RggN5da5SP9-ikMuKpY23quwaYY"

asyncio.get_event_loop().run_until_complete(send_message(token))
