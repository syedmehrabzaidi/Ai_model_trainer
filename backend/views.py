from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from bson import ObjectId
import cloudinary.uploader
from datetime import datetime
import mux_python
from mux_python.rest import ApiException
from django.http import JsonResponse
from django.conf import settings
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import requests
from publitio import PublitioAPI

from pymongo import MongoClient

from decouple import config

import stripe
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

stripe.api_key = settings.STRIPE_SECRET_KEY


# MONGO_DB_NAME = config('MONGO_DB_NAME')
# MONGO_URI = config('MONGO_URI')

# print(MONGO_DB_NAME,"----MONGO_URI---",MONGO_URI)


# MONGO_CLIENT = MongoClient(MONGO_URI)

# # Get the database
# MONGO_DB = MONGO_CLIENT[MONGO_DB_NAME]

# print(MONGO_CLIENT,"---MONGO_CLIENT-------------------------------MONGO_DB_NAME-----",MONGO_DB_NAME)


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        # try:
        if True:    
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return JsonResponse({'error': 'Email and password are required.'}, status=400)

            collection = settings.MONGO_DB['users']
            user = collection.find_one({'email': email})
            if not user:
                return JsonResponse({'error': 'Invalid email or password.'}, status=401)

            hashed_password = password
            if hashed_password != user['password']:
                return JsonResponse({'error': 'Invalid email or password.'}, status=401)

            # Store user ID in a cookie
            response = JsonResponse({'message': 'Login successful', 'user_id': str(user['_id'])}, status=200)
            # response.set_cookie(key='user_id', value=str(user['_id']), httponly=True)  # httponly for security

            return response

        # except Exception as e:
        #     return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def signup_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            subscription = data.get('subscription', False)

            if not name or not email or not password:
                return JsonResponse({'error': 'Name, email, and password are required.'}, status=400)

            # MONGO_DB = MongoClient("mongodb+srv://syedmehrab:admin123@cluster0.qyxmn12.mongodb.net/test?retryWrites=true&w=majority&ssl=true")
            # db = MONGO_DB['user']  # your database name

            # collection = db['users']  # Correctly accessing the 'users' collection


            collection = settings.MONGO_DB['users']
            # collection = MONGO_DB['users']

            existing_user = collection.find_one({'email': email})
            if existing_user:
                return JsonResponse({'error': 'A user with this email already exists.'}, status=409)

            hashed_password = password

            user_document = {
                'name': name,
                'email': email,
                'password': hashed_password,
                'subscription': subscription,
            }

            user_id = collection.insert_one(user_document).inserted_id

            # Optionally set cookie here, but not necessary if handling it in frontend
            response = JsonResponse({'message': 'User created successfully', 'user_id': str(user_id)}, status=201)

            return response

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def edit_profile_view(request):
    if request.method == 'POST':
        try:
            # Parse the request body for JSON data
            data = json.loads(request.body)
            user_id = data.get('user_id')  # Get user ID from request body
            username = data.get('name')
            email = data.get('email')
            password = data.get('password')

            if not user_id:
                return JsonResponse({'error': 'User ID is required.'}, status=401)

            # Validate input data
            if not username and not email and not password:
                return JsonResponse({'error': 'At least one field (username, email, password) must be provided.'}, status=400)

            # Access the MongoDB collection
            collection = settings.MONGO_DB['users']

            # Build the update document
            update_fields = {}
            if username:
                update_fields['name'] = username  # Assuming you have a 'username' field
            if email:
                update_fields['email'] = email
            if password:
                update_fields['password'] = password  # Note: You might want to hash the password here

            # Update the user document
            result = collection.update_one({'_id': ObjectId(user_id)}, {'$set': update_fields})

            if result.modified_count == 0:
                return JsonResponse({'error': 'No changes made. User might not exist.'}, status=404)

            return JsonResponse({'message': 'Profile updated successfully.'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def upload_video_view(request):
    if request.method == 'POST':
        try:
            # Check if a video file is included in the request
            if 'video_file' not in request.FILES:
                return JsonResponse({'error': 'No video file provided.'}, status=400)

            # Get user ID from request body
            user_id = request.POST.get('user_id')  # Directly get user ID from form data
            if not user_id:
                return JsonResponse({'error': 'User ID is required.'}, status=401)

            video_file = request.FILES['video_file']

            # Initialize Publit.io API client
            publitio_api = PublitioAPI(settings.PUBLITIO_API_KEY, settings.PUBLITIO_API_SECRET)

            # Use a context manager to open the uploaded file
            with video_file.open('rb') as video:
                # Upload the video to Publit.io
                response = publitio_api.create_file(
                    file=video,
                    title=video_file.name,  # You can customize the title if needed
                    description='Uploaded from Django'  # Customize the description if needed
                )

            # Check if the upload was successful
            if 'id' not in response or 'url_preview' not in response:
                return JsonResponse({'error': 'Failed to upload video to Publit.io.'}, status=500)

            asset_id = response['id']  # Get the asset ID for tracking
            video_url = response['url_preview']  # Get the video URL to be stored

            # Store the Publit.io asset_id, video URL, and user ID in MongoDB
            collection = settings.MONGO_DB['videos']
            date_str = datetime.today().date().strftime('%Y-%m-%d')

            video_document = {
                'user_id': ObjectId(user_id),  # Store the user ID as an ObjectId
                'asset_id': asset_id,
                'url': video_url,  # Store the video URL
                'date': date_str
            }

            # Insert the video document into the MongoDB collection
            collection.insert_one(video_document)

            # Return a success response
            return JsonResponse({
                'message': 'Video uploaded to Publit.io successfully.',
                'asset_id': asset_id,
                'url': video_url  # Include the URL in the response
            }, status=200)

        except Exception as e:
            return JsonResponse({'error': f"Unexpected error - {str(e)}"}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def delete_video_view(request):
    if request.method == 'DELETE':
        try:
            # Parse the request body for JSON data
            data = json.loads(request.body)
            user_id = data.get('user_id')  # Get user ID from request body
            if not user_id:
                return JsonResponse({'error': 'User ID is required.'}, status=401)

            # Parse the request body to get the video ID (asset_id)
            asset_id = data.get('asset_id')
            if not asset_id:
                return JsonResponse({'error': 'Video asset_id is required.'}, status=400)

            # Access the MongoDB collection
            collection = settings.MONGO_DB['videos']

            # Find the video document associated with the user and asset_id
            video = collection.find_one({'user_id': ObjectId(user_id), 'asset_id': asset_id})
            if not video:
                return JsonResponse({'error': 'Video not found or not owned by the user.'}, status=404)

            # Initialize Publit.io API client
            publitio_api = PublitioAPI(settings.PUBLITIO_API_KEY, settings.PUBLITIO_API_SECRET)

            # Delete the video from Publit.io using the asset_id
            response = publitio_api.delete_file(asset_id)

            # Check if the deletion was successful
            if response.get('success'):
                # Remove the video document from MongoDB
                collection.delete_one({'_id': video['_id']})

                # Return a success response
                return JsonResponse({'message': 'Video deleted successfully.'}, status=200)
            else:
                return JsonResponse({'error': 'Failed to delete video from Publit.io.'}, status=500)

        except Exception as e:
            return JsonResponse({'error': f"Unexpected error - {str(e)}"}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def get_videos_view(request):
    if request.method == 'GET':  # Change to handle GET request
        try:
            # Get user ID from query parameters
            user_id = request.GET.get('user_id')

            if not user_id:
                return JsonResponse({'error': 'User ID is required.'}, status=401)

            # Access the MongoDB collection
            collection = settings.MONGO_DB['videos']

            # Find all video documents associated with the user
            videos = collection.find({'user_id': ObjectId(user_id)})

            # Prepare the response list
            video_list = []
            for video in videos:
                video_list.append({
                    'url_preview': video.get('url'),  # Fetch the stored preview URL for display
                    'asset_id': video.get('asset_id'),  # Publit.io asset ID, useful for delete operations
                    'date': video.get('date')  # Optional: Include uploaded date if stored
                })

            # If no videos are found, return an empty list
            if not video_list:
                return JsonResponse({'videos': [], 'message': 'No videos found for this user.'}, status=200)

            # Return the list of videos in the response
            return JsonResponse({'videos': video_list}, status=200)

        except Exception as e:
            return JsonResponse({'error': f"Unexpected error - {str(e)}"}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
def payment_view(request):
    if request.method == "POST":
        try:
            # Parse the request body as JSON
            data = json.loads(request.body)
            amount = int(data['amount'])  # Amount is expected in cents

            # Create a PaymentIntent with the specified amount
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
            )

            # Return the client secret to confirm the payment on the frontend
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })

        except stripe.error.StripeError as e:
            # Handle Stripe errors
            return JsonResponse({'error': str(e)}, status=400)

        except Exception as e:
            # Handle general exceptions
            return JsonResponse({'error': 'Something went wrong.'}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
def subscription_view(request):
    # Your subscription logic here
    return Response({
        'message': 'This is a protected view accessible only to authenticated users.',
        'user': request.user.username
    })