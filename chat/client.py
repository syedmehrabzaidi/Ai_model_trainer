import asyncio
import websockets
import json

async def send_message(token):
    uri = f"ws://localhost:8001/ws/chat/lobby/?token={token}"
    print(f"Connecting to: {uri}")  # Debugging statement
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
token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoyMDkzNzQ5NTc1LCJpYXQiOjE3MzM3NTMxNzUsImp0aSI6IjgyNjg4OGUwMTkzMjRiM2I5ZjRmZjVlMmRiNWNjYjkzIiwidXNlcl9pZCI6IjY3NTRiNzYwNDgxMDQ4N2M5Y2JmNThkZSJ9.YW0rZR3RGT58ryJul7-5bAxvH4UAFlW6f76-vE0xACA"
print(f"Using token: {token}")  # Debugging statement

asyncio.get_event_loop().run_until_complete(send_message(token))
