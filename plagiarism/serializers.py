# plagiarism/serializers.py
from rest_framework import serializers
from .models import PlagiarismResult
from documents.serializers import SubmissionDetailSerializer

class PlagiarismResultSerializer(serializers.ModelSerializer):
    """
    PlagiarismResult serializer.
    - expose submission id and optionally nested submission detail (read-only)
    - ensure `report` is treated as JSON if the model stores JSON
    """
    submission_id = serializers.IntegerField(source='submission.id', read_only=True)
    submission_detail = SubmissionDetailSerializer(source='submission', read_only=True)
    report = serializers.JSONField(required=False)  # accept/store structured JSON report

    class Meta:
        model = PlagiarismResult
        fields = "__all__"
        read_only_fields = ["submission_id", "submission_detail", "created_at"]
