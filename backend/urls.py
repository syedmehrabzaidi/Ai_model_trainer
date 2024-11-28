"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import ( signup_view, login_view, edit_profile_view, upload_video_view, VideosView, reset_password,
                     PaymentView, SubscribedDashboardView, upload_video_view, MemberListView, ClientRequestView, ModelTrainingView,
                     AiModelView, SendMessage, FetchMessages, VerifyOtpView, TrainVideosView, Delete_video_view
                    )        
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from django.urls import re_path
# from ..chat import consumers

urlpatterns = [
    path('signup/', signup_view, name='signup_view'),
    path('login/', login_view, name='login_view'),
    # path('logout/', logout_view, name='logout_view'),
    # path('check-auth/', check_auth_view, name='check_auth_view'),
    path('edit-profile/', edit_profile_view, name='edit_profile_view'),
    path('uploadvideo/', upload_video_view.as_view(), name='upload_video'),
    path('delete-video/', Delete_video_view.as_view(), name='delete_video'),
    path('get_videos/', VideosView.as_view(), name='single-videos'),
    path('trained_videos/', TrainVideosView.as_view(), name='trained-videos'),
    path('admin/', admin.site.urls),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('forget/', reset_password, name='reset-password'),

    path('payment/', PaymentView.as_view(), name='payment_view'),
    path('sub_dashboard/', SubscribedDashboardView.as_view(), name='sub-dashboard'),
    path('members/', MemberListView.as_view(), name='member-list'),
    path('client_request/', ClientRequestView.as_view(), name='client-request'),
    path('model_training/', ModelTrainingView.as_view(), name='model-training'),
    path('ai_model_list/', AiModelView.as_view(), name='ai-model-list'),

    
    path('send-message/', SendMessage.as_view(), name='send_message'),
    path('fetch-messages/', FetchMessages.as_view(), name='fetch_messages'),
    path('otp/', VerifyOtpView.as_view(), name='otp'),

   

]
# websocket_urlpatterns = [
#     re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
# ]