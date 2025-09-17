from django.shortcuts import render
from django.utils import timezone
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

import os
from django.http import HttpResponseForbidden
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

# DRF imports
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError, PermissionDenied

# Project imports
from .models import Assignment, Submission, AssignmentReview
from .serializers import (
    AssignmentSerializer,
    SubmissionSerializer,
    SubmissionDetailSerializer,
    AssignmentReviewSerializer,
)
from users.permissions import IsProfessor, IsStudent, IsAdmin


# -------------------------------
# API: Assignments
# -------------------------------
class AssignmentListCreateView(generics.ListCreateAPIView):
    """
    GET:
      - Professors see only their assignments
      - Students/Admins see all assignments
    POST:
      - Only professors can create
    """
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "role", None) == "professor":
            return Assignment.objects.filter(professor=user)
        return Assignment.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, "role", None) != "professor":
            raise PermissionDenied("Only professors can create assignments.")
        serializer.save(professor=user)


class AssignmentReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = AssignmentReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        assignment_id = self.kwargs.get("assignment_id")
        return AssignmentReview.objects.filter(
            assignment_id=assignment_id
        ).order_by("-created_at")

    def perform_create(self, serializer):
        assignment_id = self.kwargs.get("assignment_id")
        serializer.save(student=self.request.user, assignment_id=assignment_id)


# -------------------------------
# API: Submissions
# -------------------------------
class SubmissionCreateView(generics.CreateAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        file = self.request.FILES.get("document")
        if not file:
            raise ValidationError("No file provided under key 'document'.")

        # 🔧 Match frontend: allow PDF, TXT, DOC, DOCX
        valid_extensions = [".pdf", ".txt", ".doc", ".docx"]
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in valid_extensions:
            raise ValidationError(f"Only {', '.join(valid_extensions)} are allowed.")

        # size limit
        if file.size > 10 * 1024 * 1024:
            raise ValidationError("File size exceeds 10MB limit.")

        assignment = serializer.validated_data.get("assignment")
        student = self.request.user
        if not assignment:
            raise ValidationError("Assignment must be provided.")

        # prevent duplicate
        if Submission.objects.filter(student=student, assignment=assignment).exists():
            raise ValidationError("You have already submitted for this assignment.")

        # deadline check
        if assignment.deadline and timezone.now() > assignment.deadline:
            raise ValidationError("Deadline has passed. Submission not allowed.")

        serializer.save(student=student)

    def get(self, request, *args, **kwargs):
        return Response({
            "message": "This is the submission upload endpoint.",
            "usage": "POST multipart/form-data with fields: assignment (id), document (file).",
            "example": {"assignment": 1, "document": "upload_file.pdf"}
        })


class SubmissionListView(generics.ListAPIView):
    serializer_class = SubmissionDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Submission.objects.all()
        user = self.request.user
        mine = self.request.query_params.get("mine")

        if mine in ("1", "true", "True") and user.is_authenticated:
            return Submission.objects.filter(student=user)

        if getattr(user, "role", None) == "professor":
            return Submission.objects.filter(assignment__professor=user)

        return qs


class StudentSubmissionListView(generics.ListAPIView):
    serializer_class = SubmissionDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def get_queryset(self):
        return Submission.objects.filter(student=self.request.user)


class ProfessorSubmissionListView(generics.ListAPIView):
    serializer_class = SubmissionDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsProfessor]

    def get_queryset(self):
        return Submission.objects.filter(assignment__professor=self.request.user)


class AdminSubmissionListView(generics.ListAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]


class AdminAssignmentUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAdmin]


class AdminSubmissionUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsAdmin]


# -------------------------------
# HTML Page Views (Frontend)
# -------------------------------


@login_required
def student_page(request):
    """Unified Student Dashboard (assignments + submissions)."""
    if getattr(request.user, "role", None) != "student":
        return render(request, "403.html", status=403)
    return render(request, "student.html")


@login_required
def professor_page(request):
    """Unified Professor Dashboard (assignments + submissions)."""
    if getattr(request.user, "role", None) != "professor":
        return render(request, "403.html", status=403)
    return render(request, "professor.html")