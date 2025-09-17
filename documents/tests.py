from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase
from django.urls import reverse
from users.models import User
from documents.models import Assignment
from django.utils import timezone
from datetime import timedelta

class AssignmentTests(APITestCase):
    def setUp(self):
        self.professor = User.objects.create_user(username="prof", password="prof123", role="professor")
        self.client.force_authenticate(user=self.professor)

    def test_create_assignment(self):
        url = reverse("assignment_list")  # name in urls.py
        data = {"title": "Assignment 1", "description": "Test description", "deadline": (timezone.now() + timedelta(days=7)).isoformat()}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Assignment.objects.count(), 1)
