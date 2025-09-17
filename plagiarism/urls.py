# plagiarism/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Run a plagiarism check (POST) /info (GET)
    path('check/<int:submission_id>/', views.PlagiarismCheckView.as_view(), name='plagiarism_check'),

    # Results listing and detail (detail lookup by submission_id)
    path('results/', views.PlagiarismResultListView.as_view(), name='plagiarism_results'),
    path('results/<int:submission_id>/', views.PlagiarismResultView.as_view(), name='plagiarism_result'),
]
