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
from .views import signup_view, login_view, edit_profile_view, upload_video_view, delete_video_view, get_videos_view, payment_view, reset_password
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('signup/', signup_view, name='signup_view'),
    path('login/', login_view, name='login_view'),
    # path('logout/', logout_view, name='logout_view'),
    # path('check-auth/', check_auth_view, name='check_auth_view'),
    path('edit-profile/', edit_profile_view, name='edit_profile_view'),
    path('upload-video/', upload_video_view, name='upload_video'),
    path('delete-video/', delete_video_view, name='delete_video'),
    path('get-videos/', get_videos_view, name='get_videos'),
    path('admin/', admin.site.urls),

    path('payment/', payment_view, name='payment_view'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('forget/', reset_password, name='reset-password'),

]
