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

def generate_jwt_tokens(user_id):
    refresh = RefreshToken()
    refresh['user_id'] = user_id
    access_token = refresh.access_token
    access_token['user_id'] = user_id
    return {
        'refresh': str(refresh),
        'access': str(access_token),
    }
