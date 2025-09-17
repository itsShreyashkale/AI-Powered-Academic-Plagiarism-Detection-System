from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase
from django.urls import reverse
from users.models import User

class UserTests(APITestCase):
    def test_register_and_login(self):
        url = reverse("register")
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test@1234",
            "password2": "Test@1234",
            "role": "student"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)

        login_url = reverse("login")
        response = self.client.post(login_url, {"username": "testuser", "password": "Test@1234"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
