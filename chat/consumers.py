# chat/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging
from django.conf import settings
import jwt
from bson import ObjectId

logger = logging.getLogger(__name__)

class SimpleUser:
    def __init__(self, user):
        self._id = user['_id']
        self.name = user['name']
        self.admin = user.get('admin', False)

class CustomJWTAuthentication:
    def get_validated_token(self, token):
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise jwt.InvalidTokenError("Token has expired")
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError("Invalid token")

    def get_user(self, validated_token):
        user_id = validated_token['user_id']
        print(f"---------------------User ID from token: {user_id}")  # Debugging statement
        collection = settings.MONGO_DB['users']
        user = collection.find_one({'_id': ObjectId(user_id)})
        print(f"------------------------User from MongoDB: {user}")  # Debugging statement
        if not user:
            raise jwt.InvalidTokenError('User not found')

        # Return a user-like object
        return SimpleUser(user)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Extract JWT token from query params
        query_params = self.scope['query_string'].decode()
        token = query_params.split('token=')[-1]

        # Authenticate user using CustomJWTAuthentication
        jwt_auth = CustomJWTAuthentication()
        try:
            validated_token = jwt_auth.get_validated_token(token)
            self.user = jwt_auth.get_user(validated_token)
            self.user_name = self.user.name
            self.is_admin = self.user.admin
            print(self.user_name,"------self.user_name-----------------------------self.is_admin-----------",self.is_admin)
        except jwt.InvalidTokenError:
            logger.error("Invalid token")
            await self.close()

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"WebSocket connected: {self.room_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected: {self.room_name}")

    async def receive(self, text_data):
        if text_data:
            try:
                text_data_json = json.loads(text_data)
                message = text_data_json['message']

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'user_name': self.user_name,
                        'is_admin': self.is_admin
                    }
                )
                logger.info(f"Message received: {message}")
            except json.JSONDecodeError:
                logger.error("Received invalid JSON")
        else:
            logger.error("Received empty message")

    async def chat_message(self, event):
        message = event['message']
        user_name = event['user_name']
        is_admin = event['is_admin']

        await self.send(text_data=json.dumps({
            'message': message,
            'user_name': user_name,
            'is_admin': is_admin
        }))
        logger.info(f"Message sent: {message}")
