# plagiarism/views.py
from django.shortcuts import render
from django.db import connection
import time
import logging
import os

# DRF imports
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Project imports
from .models import PlagiarismResult
from .serializers import PlagiarismResultSerializer
from documents.models import Submission
from .utils import (
    extract_matching_sentences,
    extract_text_from_file,
    calculate_similarity,
    calculate_semantic_similarity
)
from users.permissions import IsProfessor, IsAdmin

# Module-level logger
logger = logging.getLogger(__name__)


def ensure_prof_or_admin(request):
    """
    Helper: ensure the request.user is a professor or admin.
    Returns None when allowed, or a DRF Response(403) when denied.
    """
    user = getattr(request, "user", None)
    role = getattr(user, "role", None)
    if role in ("professor", "admin"):
        return None
    return Response({"detail": "You do not have permission to perform this action."},
                    status=status.HTTP_403_FORBIDDEN)


# -------------------------------
# Run plagiarism check on a submission
# -------------------------------
class PlagiarismCheckView(generics.GenericAPIView):
    """
    POST /api/plagiarism/check/<submission_id>/
      - Accepts JSON { "algorithm": "TF-IDF" | "BERT" } (default TF-IDF)
      - Compares submission text to other submissions for the same assignment
      - Stores/updates PlagiarismResult and returns:
          { "result": {...}, "latency_seconds": 0.123, "db_queries": 5 }
    GET returns a small usage message.
    """
    serializer_class = PlagiarismResultSerializer
    permission_classes = [IsAuthenticated]  # runtime role-check performed below

    def get(self, request, submission_id):
        return Response({
            "message": "This endpoint checks plagiarism for a submission.",
            "usage": f"Send a POST request to /api/plagiarism/check/{submission_id}/ with {{'algorithm': 'TF-IDF' or 'BERT'}}",
            "example": {"algorithm": "BERT"}
        })

    def post(self, request, submission_id):
        # Role check: only professor/admin allowed to run checks
        denied = ensure_prof_or_admin(request)
        if denied:
            return denied

        user = request.user
        logger.info(f"Plagiarism check triggered by {user.username} (role: {getattr(user,'role',None)}) for submission {submission_id} at {time.strftime('%Y-%m-%d %H:%M:%S')}")

        start_time = time.time()
        queries_before = len(connection.queries)

        # Load the submission and its file safely
        try:
            submission = Submission.objects.get(id=submission_id)
        except Submission.DoesNotExist:
            logger.info(f"Submission {submission_id} not found")
            return Response({"error": "Submission not found"}, status=status.HTTP_404_NOT_FOUND)

        if not getattr(submission, "document", None):
            logger.error(f"Submission {submission_id} has no attached document.")
            return Response({"error": "Submission has no document file."}, status=status.HTTP_400_BAD_REQUEST)

        # Extract text
        try:
            file_path = submission.document.path
            if not os.path.exists(file_path):
                logger.error(f"File path does not exist for submission {submission_id}: {file_path}")
                return Response({"error": "Submission file not found on disk."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            new_doc_text = extract_text_from_file(file_path)
        except Exception:
            logger.exception("Error extracting text from file for submission %s", submission_id)
            return Response({"error": "Failed to extract text from submission file."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Compare against other submissions in same assignment
        other_submissions = Submission.objects.filter(assignment=submission.assignment).exclude(id=submission.id)

        # Short-circuit if no other submissions
        if not other_submissions.exists():
            similarity = 0.0
            detailed_report = []
        else:
            # Extract texts (skip problematic files)
            existing_docs = []
            for s in other_submissions:
                try:
                    txt = extract_text_from_file(s.document.path)
                    existing_docs.append(txt)
                except Exception:
                    logger.exception("Failed to extract text from submission %s (skipping)", s.id)
                    continue

            if len(existing_docs) == 0:
                similarity = 0.0
            else:
                algorithm = request.data.get("algorithm", "TF-IDF")
                try:
                    if algorithm == "BERT":
                        similarity = calculate_semantic_similarity(new_doc_text, existing_docs)
                    else:
                        similarity = calculate_similarity(new_doc_text, existing_docs)
                    # normalize similarity to float in [0,1]
                    try:
                        similarity = float(similarity)
                    except Exception:
                        similarity = 0.0
                except Exception:
                    logger.exception("Error during similarity computation for submission %s", submission_id)
                    similarity = 0.0

            # Build detailed matching report (per other submission)
            detailed_report = []
            for other in other_submissions:
                try:
                    other_text = extract_text_from_file(other.document.path)
                    matches = extract_matching_sentences(new_doc_text, other_text)
                    if matches:
                        detailed_report.append({
                            "compared_with": other.id,
                            "matches": matches
                        })
                except Exception:
                    # skip problematic entries
                    continue

        # Persist result
        try:
            result_obj, created = PlagiarismResult.objects.update_or_create(
                submission=submission,
                defaults={
                    "similarity_score": similarity * 100 if similarity is not None else 0.0,
                    "compared_with": ",".join([str(s.id) for s in other_submissions]) if other_submissions.exists() else "",
                    "algorithm": request.data.get("algorithm", "TF-IDF"),
                    "report": detailed_report
                }
            )
        except Exception:
            logger.exception("Failed to save plagiarism result for submission %s", submission_id)
            return Response({"error": "Failed to persist plagiarism result."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Benchmark
        queries_after = len(connection.queries)
        latency = round(time.time() - start_time, 3)
        db_queries = queries_after - queries_before

        serialized = PlagiarismResultSerializer(result_obj).data

        logger.info("PlagiarismResult saved for submission %s — score: %.2f%% — latency: %.3fs — db_queries: %d",
                    submission_id, serialized.get("similarity_score", 0.0), latency, db_queries)

        return Response({
            "result": serialized,
            "latency_seconds": latency,
            "db_queries": db_queries
        }, status=status.HTTP_200_OK)


# -------------------------------
# Plagiarism results listing (added)
# -------------------------------
class PlagiarismResultListView(generics.ListAPIView):
    """
    List stored plagiarism results.
      - admin: see all
      - professor: see results for their assignments' submissions
      - student: see results for their own submissions
    """
    queryset = PlagiarismResult.objects.all()
    serializer_class = PlagiarismResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user, "role", None)
        if role == "admin":
            return PlagiarismResult.objects.all().order_by("-id")
        if role == "professor":
            return PlagiarismResult.objects.filter(submission__assignment__professor=user).order_by("-id")
        if role == "student":
            return PlagiarismResult.objects.filter(submission__student=user).order_by("-id")
        return PlagiarismResult.objects.none()


# -------------------------------
# Get plagiarism result for a submission
# -------------------------------
class PlagiarismResultView(generics.RetrieveAPIView):
    """
    Retrieve a plagiarism result by submission_id.
    Uses lookup_field = 'submission_id' so DRF will query PlagiarismResult.objects.get(submission_id=<value>).
    """
    queryset = PlagiarismResult.objects.all()
    serializer_class = PlagiarismResultSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # enforce professor/admin/students as implemented in list view
        # only allow the same role logic as list view: student can view own results
        user = request.user
        role = getattr(user, "role", None)
        submission_id = kwargs.get("submission_id")
        if role == "professor":
            # ensure professor owns the assignment of this submission
            if not PlagiarismResult.objects.filter(submission__id=submission_id, submission__assignment__professor=user).exists():
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        elif role == "student":
            if not PlagiarismResult.objects.filter(submission__id=submission_id, submission__student=user).exists():
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        elif role == "admin":
            pass  # admin can view any
        else:
            return Response({"detail": "You do not have permission to view this."}, status=status.HTTP_403_FORBIDDEN)

        return super().get(request, *args, **kwargs)

    lookup_field = "submission_id"


# simple page view functions (render templates from /templates/)
def index(request):
    return render(request, "index.html")

def login_view(request):
    return render(request, "users/login.html")

def register_view(request):
    return render(request, "users/register.html")

def profile_view(request):
    return render(request, "users/profile.html")

def assignments_view(request):
    return render(request, "documents/assignments.html")

def submissions_view(request):
    return render(request, "documents/submission.html")

def plagiarism_check_view(request):
    return render(request, "plagiarism/check.html")

def plagiarism_result_view(request):
    return render(request, "plagiarism/result.html")