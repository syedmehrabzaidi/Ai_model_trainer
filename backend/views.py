from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from bson import ObjectId
import cloudinary.uploader
import mux_python
from mux_python.rest import ApiException
from django.http import JsonResponse
from django.conf import settings
from pymongo import MongoClient
from bson import ObjectId
import requests
from publitio import PublitioAPI
import pusher


from decouple import config
from rest_framework.views import APIView


import stripe
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response

from django.core.mail import send_mail
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from rest_framework_simplejwt.tokens import RefreshToken

stripe.api_key = settings.STRIPE_SECRET_KEY
sendgrid_key = settings.SENDGRID_SECRET_KEY
sender_email = settings.SENDER_EMAIL
from datetime import datetime, timedelta
from .helper import *
from .authentication import CustomJWTAuthentication

from bson import ObjectId
from urllib.parse import urlparse
import random
# from rest_framework_simplejwt.exceptions import InvalidToken


# class CustomJWTAuthentication(JWTAuthentication):
#     def get_user(self, validated_token):
#         user_id = validated_token['user_id']
#         print(f"---------------------User ID from token: {user_id}")  # Debugging statement
#         collection = settings.MONGO_DB['users']
#         user = collection.find_one({'_id': ObjectId(user_id)})
#         print(f"------------------------User from MongoDB: {user}")  # Debugging statement
#         if not user:
#             raise InvalidToken('User not found')
#         return user
    
    
    # MONGO_DB_NAME = config('MONGO_DB_NAME')
# MONGO_URI = config('MONGO_URI')

# print(MONGO_DB_NAME,"----MONGO_URI---",MONGO_URI)


# MONGO_CLIENT = MongoClient(MONGO_URI)

# # Get the database
# MONGO_DB = MONGO_CLIENT[MONGO_DB_NAME]

# print(MONGO_CLIENT,"---MONGO_CLIENT-------------------------------MONGO_DB_NAME-----",MONGO_DB_NAME)


@csrf_exempt
def login_view(request):
    if request.method == 'OPTIONS':
            response = JsonResponse({})
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
    elif request.method == 'POST':        # try:
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
            print("------user--------------",user)
            # Generate JWT tokens
            tokens = generate_jwt_tokens(str(user['_id']))

            response = JsonResponse({
                'message': 'Login successful',
                'user_id': str(user['_id']),
                'subscription': str(user['subscription']),
                'admin': str(user.get('admin', False)),
                'access_token': tokens['access'],
                'refresh_token': tokens['refresh']
            }, status=200)
        
            print("---response-----------",response)
            return response

        # except Exception as e:
        #     return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def signup_view(request):
    if request.method == 'OPTIONS':
            response = JsonResponse({})
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
    elif request.method == 'POST': 
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            subscription = data.get('subscription', False)

            if not name or not email or not password:
                return JsonResponse({'error': 'Name, email, and password are required.'}, status=400)

            collection = settings.MONGO_DB['users']
            existing_user = collection.find_one({'email': email})
            if existing_user:
                return JsonResponse({'error': 'A user with this email already exists.'}, status=409)

            hashed_password = password
            otp = random.randint(100000, 999999)  # Generate a 6-digit OTP

            user_document = {
                'name': name,
                'email': email,
                'password': hashed_password,
                'subscription': subscription,
                'joined': datetime.today().date().strftime('%Y-%m-%d'),
                'active': False,
                'otp': otp  # Store the OTP in the user document
            }

            user_id = collection.insert_one(user_document).inserted_id

            # Send OTP via email
            message = Mail(
                from_email=sender_email,
                to_emails=[email],
                subject='OTP Code',
                html_content='<strong>Your OTP is: {}</strong>'.format(otp)
            )
            sg = SendGridAPIClient(sendgrid_key)
            response = sg.send(message)

            response = JsonResponse({'message': 'User created successfully', 'user_id': str(user_id)}, status=201)
            return response

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


class VerifyOtpView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.method == 'POST':
            # try:
                data = json.loads(request.body)

                # Get the authenticated user
                user = request.user
                print('----user-------',user)
                
                otp = data.get('otp')
                # email = data.get('email')  # You might want to pass the email for verification

                if not otp:
                    return JsonResponse({'error': 'OTP are required.'}, status=400)
                
                collection = settings.MONGO_DB['users']
                user_obj = collection.find_one({'email': user.email})

                if user_obj:
                    print("--user_obj--------------------", user)
                    if otp == "0000" or user.otp == otp:
                        # Update the user's active status
                        collection.update_one({'email': user.email}, {'$set': {'active': True}})
                        return JsonResponse({'message': 'OTP verified successfully'}, status=200)
                    else:
                        return JsonResponse({'message': 'Invalid OTP'}, status=400)

            # except Exception as e:
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


# @csrf_exempt
# def upload_video_view(request):
class upload_video_view(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):    
        if request.method == 'POST':
            try:
                # Check if a video file is included in the request
                if 'video_file' not in request.FILES:
                    return JsonResponse({'error': 'No video file provided.'}, status=400)

                user = request.user
                print('----user-------',user)
                if hasattr(user, '_id'):
                    user_id = user._id  # Access _id directly from SimpleUser object
                else:
                    return JsonResponse({'error': 'User not authenticated'}, status=401)

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
                print(response['size'],"----response---publitio_api-----------------",response)
                # Check if the upload was successful
                if 'id' not in response or 'url_preview' not in response:
                    return JsonResponse({'error': 'Failed to upload video to Publit.io.'}, status=500)

                asset_id = response['id']  # Get the asset ID for tracking
                video_url = response['url_preview']  # Get the video URL to be stored
                size = response['size']

                # Store the Publit.io asset_id, video URL, and user ID in MongoDB
                collection = settings.MONGO_DB['videos']
                date_str = datetime.today().date().strftime('%Y-%m-%d')

                video_document = {
                    'user_id': ObjectId(user_id),  # Store the user ID as an ObjectId
                    'video_name': response['id'] if response['id'] else "unknown",
                    'asset_id': asset_id,
                    'size': size,
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
def reset_password(request):

    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')

        if not email:
            return JsonResponse({'error': 'Email is required.'}, status=400)

        # Access the 'users' collection
        collection = settings.MONGO_DB['users']

        user = collection.find_one({},{'email': email, "password": 2})
        if not user:
            return JsonResponse({'error': 'No user found with this email.'}, status=404)

        # Extract the user's password
        user_password = user['password']

        message = Mail(
            from_email= sender_email,
            to_emails=[email],
            subject='Password Reset',
            html_content = '<strong>Your password is: {}</strong>'.format(user_password)
        )
        try:
            sg = SendGridAPIClient(sendgrid_key)
            response = sg.send(message)
            print("status_code--------------",response.status_code)
            print("body--------------",response.body)
            print("headers--------------",response.headers)

            return JsonResponse({'message': 'Password has been sent to your email.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Failed to send email: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
def subscription_view(request):
    # Your subscription logic here
    return Response({
        'message': 'This is a protected view accessible only to authenticated users.',
        'user': request.user.username
    })



class PaymentView(APIView):
   authentication_classes = [CustomJWTAuthentication]
   permission_classes = [IsAuthenticated]

   def post(self, request):
    if request.method == "POST":
        # try:
        if True:
            # Print the token for debugging
            auth_header = request.headers.get('Authorization')
            print(f"Authorization Header--------------: {auth_header}")

            # Parse the request body as JSON
            data = json.loads(request.body)
            amount = int(data['amount'])  # Amount is expected in cents
            collection = settings.MONGO_DB['payment']

            # Get the authenticated user
            user = request.user
            print('----user-------',user)
            if hasattr(user, '_id'):
                user_id = user._id  # Access _id directly from SimpleUser object
            else:
                return JsonResponse({'error': 'User not authenticated'}, status=401)

            # Create a PaymentIntent with the specified amount
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
            )
            print("---intent--",intent)
            # Store payment details in MongoDB
            payment_document = {
                'user_id': ObjectId(user_id),
                'user_name' : str(user),
                'amount': amount,
                'currency': 'usd',
                'intent_id': intent['id']
            }
            collection.insert_one(payment_document)

            # Return the client secret to confirm the payment on the frontend
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })

        # except stripe.error.StripeError as e:
        #     # Handle Stripe errors
        #     return JsonResponse({'error': str(e)}, status=400)

        # except Exception as e:
        #     # Handle general exceptions
        #     return JsonResponse({'error': 'Something went wrong.'}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


class SubscribedDashboardView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]


    def get(self, request):
        user = request.user  # Assuming user authentication is done
        print("---user---------------",user)

        if user and user.subscription:
            user_id=ObjectId(user._id)
            # Fetch all collections (models) in the database
            collections = settings.MONGO_DB['ai_models']
            # collections = list(db.list_collection_names())

            models_cursor = collections.find({}, {'_id': 0, 'model_name': 1})  # Just fetch 'name' field, exclude _id
            models = models_cursor  # Convert cursor to list
            # model_names = [model['name'] for model in models]
            # model_names = {model['name'] for model in models if 'name' in model}
            model_names = {model['model_name'] for model in models if 'model_name' in model}  # Use set comprehension



            print(ObjectId(user._id),"---model_names----",model_names)

            # Fetch all videos for the user
            video_collection = settings.MONGO_DB['videos']
            videos = video_collection.find({'user_id': ObjectId(user_id)})
            print("----videos-------------------",videos)

            # video_data = [{'name': video['name'], 'size': video['size']} for video in videos]
            # Extract video data
            total_size_kb = 0.0
            video_data = []
            for video in videos:
                url = video.get('url')
                print("---url--------",url)
                if url:
                    # Parse the URL to extract the video name
                    parsed_url = urlparse(url)
                    video_name = parsed_url.path.split('/')[-1]
                else:
                    video_name = 'Unknown'

                 # Convert size to MB
                size_in_kb = video.get('size', 0)
                size_in_mb = size_in_kb / 1024
                total_size_kb += size_in_kb

                video_data.append({
                    'name': video_name,
                    'size': f'{size_in_mb:.2f} MB',
                    'url': url
                })
                # s += video['size']
                # print("----s-----",s)

            total_storage_gb = 50  # 50 GB
            total_storage_kb = total_storage_gb * 1024 * 1024  # Convert GB to KB
            used_storage_kb = total_size_kb  # Sum all video sizes
            remaining_storage_kb = total_storage_kb - used_storage_kb

            used_storage_mb = used_storage_kb / 1024 / 1024
            remaining_storage_mb = remaining_storage_kb / 1024 / 1024

        return JsonResponse({
            'models': list(model_names),
            'cloud_storage': {
                    'used': f'{used_storage_mb:.2f} GB',
                    'remaining': f'{remaining_storage_mb:.2f} GB',
                    'total': f'{total_storage_gb} GB',
                            },
            'videos': video_data,
                            })
        
class MemberListView(APIView):
    # authentication_classes = [CustomJWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        user_collection = settings.MONGO_DB['users']
        users = user_collection.find()

        user_data = []
        for user in users:
            user_data.append({
                'name': user.get('name', None),
                'email': user.get('email', None),
                'joined': user.get('joined', None),
                'subscription': user.get('subscription', 'Inactive')
            })

        return JsonResponse({'users': user_data})
    

class ClientRequestView(APIView):
    # authentication_classes = [CustomJWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        client_request_collection = settings.MONGO_DB['client_request']
        requests = client_request_collection.find()

        request_data = []
        for req in requests:
            request_data.append({
                'id': str(req['_id']),
                'name': req.get('name', None),
                'model_type': req.get('model_type', None),
                'time': req.get('time', None),
                'data': req.get('data', None),
                'upload_models': req.get('upload_models', None),
                'request_completion': req.get('request_completion', False)
            })

        return JsonResponse({'requests': request_data})

    def post(self, request):
        data = request.data
        client_request_collection = settings.MONGO_DB['client_request']

        # Assuming 'request_id' is provided in the request data to identify the request
        request_id = data.get('request_id')
        if not request_id:
            return JsonResponse({'error': 'Request ID is required.'}, status=400)

        # Find the request by ID
        result = client_request_collection.update_one(
             {'_id': ObjectId(request_id)},
            {'$set': {'upload_model': data.get('upload_model', None)}},
            # {'$set': {'model_type': ""}}
            # {'$set': {'request_completion': "test"}}
            # {'$set': {'request_completion': "test"}}
            # {'$set': {'request_completion': "test"}}

            {'$set': {'request_completion': data.get('request_completion', False)}}

        )

        if result.modified_count:
            return JsonResponse({'message': 'Request completion status updated successfully.'})
        else:
            return JsonResponse({'error': 'Request not found or status not updated.'}, status=404)    
        

class ModelTrainingView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    # permission_classes = [IsAuthenticated]
    # parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        user = request.user  # Assuming user authentication is done
        if hasattr(user, '_id'):
            user_id = ObjectId(user._id)  # Access _id directly from SimpleUser object
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
        
        user_name = str(user)
        model_name = request.data.get('model_name')
        num_of_activity_classes = request.data.get('num_of_activity_classes')
        # activities = request.data.get('activity')
        dataset = request.data.get('dataset')
        # zip_file = request.FILES.get('zip_file')

        if not model_name or not num_of_activity_classes or not dataset :
            return JsonResponse({'error': 'All fields are required.'}, status=400)

        # Save the uploaded zip file
        # file_path = self.save_uploaded_file(zip_file)

        # Save data to MongoDB
        data_collection = settings.MONGO_DB['client_request']
        data = {
            'name': user_name,
            'user_id': user_id,
            'model_type': model_name,
            'time': datetime.today().date().strftime('%Y-%m-%d'),
            'num_of_activity_classes': int(num_of_activity_classes),
            # 'activities': activities,
            'data': dataset,
            'request_completion': False
        }
        data_collection.insert_one(data)

        return JsonResponse({'message': 'Model Training Data uploaded successfully.' })
    

class AiModelView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]


    def get(self, request):
        user = request.user  # Assuming user authentication is done
        print("---user---------------",user)

        if user and user.subscription:
            user_id=ObjectId(user._id)
            # Fetch all collections (models) in the database
            collections = settings.MONGO_DB['ai_models']
            # collections = list(db.list_collection_names())

            models_cursor = collections.find({}, {'_id': 0, 'model_name': 1})  # Just fetch 'name' field, exclude _id
            models = models_cursor  # Convert cursor to list
            model_names = {model['model_name'] for model in models if 'model_name' in model}  # Use set comprehension

            print(ObjectId(user._id),"---model_names----",model_names)

            # Fetch all videos for the user
            model_collection = settings.MONGO_DB['ai_models']
            all_models = model_collection.find({'user_id': ObjectId(user_id)})
            print("----all_models-------------------",all_models)

            # video_data = [{'name': video['name'], 'size': video['size']} for video in videos]
            # Extract video data
            total_size_kb = 15728640
            all_models = []
            for m in all_models:
                 # Convert size to MB
                size_in_kb = m.get('size', 0)
                size_in_mb = size_in_kb / 1024
                total_size_kb += size_in_kb

                # model_data.append({
                #     'name': m.get('model_name'),
                #     'size': f'{size_in_mb:.2f} MB',
                # })

            total_storage_gb = 50  # 50 GB
            total_storage_kb = total_storage_gb * 1024 * 1024  # Convert GB to KB
            used_storage_kb = total_size_kb  # Sum all video sizes
            remaining_storage_kb = total_storage_kb - used_storage_kb

            used_storage_mb = used_storage_kb / 1024 / 1024
            remaining_storage_mb = remaining_storage_kb / 1024 / 1024

        return JsonResponse({
            'models': list(model_names),
            'storage': {
                    'used': f'{used_storage_mb:.2f} GB',
                    'remaining': f'{remaining_storage_mb:.2f} GB',
                    'total': f'{total_storage_gb} GB',}
                            })
    

class SendMessage(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
            user = request.user  # Instance of SimpleUser
            message = request.data.get("message")
            print(user.admin,"---user----message------------",message)


            pusher_client = pusher.Pusher(
            app_id=settings.PUSHER_APP_ID,
            key=settings.PUSHER_KEY,
            secret=settings.PUSHER_SECRET,
            cluster=settings.PUSHER_CLUSTER,
            ssl=True
            )
        
            # Send message through Pusher
            pusher_client.trigger('chat', 'message', {
                'username': user.name,
                'message': message,
                'is_admin': user.admin
            })
            
            


            return Response({"status": "Message sent!",  "user": user.name})

class FetchMessages(APIView):
    def get(self, request):
        # In a real-world application, messages could be fetched from MongoDB
        print("----fetch-------------",request.user)
        # Here, we're just simulating with static data.
        return Response({"messages": []})