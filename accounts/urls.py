from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from accounts.views import *

app_name = 'accounts'


urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='login_refresh'),
    path('get-session/', SessionView.as_view(), name='get_session'),
    path('register/', RegisterUserView.as_view(), name="register"),
    path('contacts/', ContactsAPIView.as_view(), name="contacts")

]