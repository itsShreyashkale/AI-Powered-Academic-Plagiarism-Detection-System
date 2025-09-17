# users/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, UserDetailView, UserListView, CustomLoginView, PasswordResetView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),        # uses your CustomLoginView (GET info + POST tokens)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserDetailView.as_view(), name='user_detail'),
    path('list/', UserListView.as_view(), name='user_list'),
    path('reset-password/', PasswordResetView.as_view(), name='reset_password'),
]
