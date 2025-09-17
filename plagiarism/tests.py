from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

# DRF test imports
from rest_framework.test import APITestCase
from django.urls import reverse
from users.models import User
from documents.models import Assignment, Submission
from django.core.files.uploadedfile import SimpleUploadedFile


class PlagiarismTests(APITestCase):
    def setUp(self):
        # Create professor & student
        self.prof = User.objects.create_user(username="prof", password="prof123", role="professor")
        self.student = User.objects.create_user(username="stud", password="stud123", role="student")

        # Create assignment with deadline
        self.assignment = Assignment.objects.create(
            title="A1",
            description="Test",
            professor=self.prof,
            deadline=timezone.now() + timedelta(days=7)
        )

        # Create two submissions for comparison
        file1 = SimpleUploadedFile("file1.txt", b"Hello world submission")
        self.submission1 = Submission.objects.create(
            assignment=self.assignment, student=self.student, document=file1
        )

        file2 = SimpleUploadedFile("file2.txt", b"Hello different submission")
        self.submission2 = Submission.objects.create(
            assignment=self.assignment, student=self.student, document=file2
        )

        # Authenticate as professor
        self.client.force_authenticate(user=self.prof)

    def test_plagiarism_check(self):
        # ✅ use submission1 instead of non-existent self.submission
        url = reverse("plagiarism_check", args=[self.submission1.id])
        response = self.client.post(url, {"algorithm": "TF-IDF"}, format="json")

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("result", response.data)  # ✅ fixed typo
        self.assertIn("similarity_score", response.data["result"])
