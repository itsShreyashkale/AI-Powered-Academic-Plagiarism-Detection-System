from django.urls import path
from . import views
from .views import (
    AssignmentListCreateView,
    SubmissionCreateView,
    SubmissionListView,
    StudentSubmissionListView,
    ProfessorSubmissionListView,
    AdminSubmissionListView,
    AdminAssignmentUpdateDeleteView,
    AdminSubmissionUpdateDeleteView,
    AssignmentReviewListCreateView,
)

urlpatterns = [
    # -------------------------------
    # Assignment endpoints
    # -------------------------------
    path("assignments/", AssignmentListCreateView.as_view(), name="assignment_list"),
    path("assignments/<int:pk>/", AdminAssignmentUpdateDeleteView.as_view(), name="assignment-detail"),
    path("assignments/<int:assignment_id>/reviews/", AssignmentReviewListCreateView.as_view(), name="assignment-reviews"),

    # -------------------------------
    # Submission endpoints
    # -------------------------------
    path("submissions/", SubmissionListView.as_view(), name="submission-list"),               # GET (all / professor / student depending on role)
    path("submissions/create/", SubmissionCreateView.as_view(), name="submission-create"),    # POST multipart upload
    path("submissions/<int:pk>/", AdminSubmissionUpdateDeleteView.as_view(), name="submission-detail"),
    path("submissions/mine/", StudentSubmissionListView.as_view(), name="submission-mine"),

    # Convenience role-based submission lists
    path("submissions/student/", StudentSubmissionListView.as_view(), name="student-submissions"),
    path("submissions/professor/", ProfessorSubmissionListView.as_view(), name="professor-submissions"),
    path("submissions/admin/", AdminSubmissionListView.as_view(), name="admin-submissions"),

    # -------------------------------
    # Frontend pages (merged)
    # -------------------------------
    path("pages/student/", views.student_page, name="student-page"),
    path("pages/professor/", views.professor_page, name="professor-page"),
]
