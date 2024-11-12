# chat_project/settings.py

INSTALLED_APPS = [
    ...
    'channels',
    'chat',
]

ASGI_APPLICATION = 'chat.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Add your MongoDB settings
MONGO_DB = {
    'users': 'user',
}

# Add your secret key
SECRET_KEY = 'your_secret_key_here'
