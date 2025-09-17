from django.shortcuts import render

# DRF imports
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

# JWT
from rest_framework_simplejwt.views import TokenObtainPairView

# Django user
from django.contrib.auth import get_user_model

# Project imports
from .serializers import RegisterSerializer, UserSerializer
from .permissions import IsProfessor, IsStudent, IsAdmin

User = get_user_model()


# -------------------------------
# Register new users
# -------------------------------
class RegisterView(generics.CreateAPIView):
    """
    POST: Register a new user.
    GET: Simple informational response for browser/developers.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({
            "message": "This is the register endpoint.",
            "usage": "Send a POST request with {username, email, password, password2, role} to register.",
            "example": {
                "username": "alice",
                "email": "alice@example.com",
                "password": "Test@1234",
                "password2": "Test@1234",
                "role": "student"
            }
        })


# -------------------------------
# Get user details (Profile)
# -------------------------------
class UserDetailView(generics.RetrieveAPIView):
    """
    Returns profile info for the currently authenticated user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Return the logged-in user regardless of provided pk
        return self.request.user


# -------------------------------
# Admin can list all users
# -------------------------------
class UserListView(generics.ListAPIView):
    """
    Admin-only listing of users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


# -------------------------------
# Login view (JWT tokens)
# -------------------------------
class CustomLoginView(TokenObtainPairView):
    """
    Uses SimpleJWT's TokenObtainPairView to provide POST /api/users/login/ (username/password → access+refresh).
    Adding GET to provide a human-readable information response for browser testing.
    """
    # TokenObtainPairView already exposes POST handling; only add GET for info
    def get(self, request, *args, **kwargs):
        return Response({
            "message": "This is the login endpoint.",
            "usage": "Send a POST request with {username, password} to get JWT tokens.",
            "example": {
                "username": "john",
                "password": "Test@1234"
            }
        })


# -------------------------------
# Simple Password Reset (DEV helper)
# -------------------------------
class PasswordResetView(APIView):
    """
    Warning: This is a simple password-reset endpoint intended for development/testing.
    In production you should implement a secure reset flow (email token, rate limiting, logging).
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "message": "Send a POST request with {username, new_password} to reset password."
        })

    def post(self, request):
        username = request.data.get("username")
        new_password = request.data.get("new_password")

        if not username or not new_password:
            return Response({"error": "username and new_password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            return Response({"status": "Password reset successful"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
