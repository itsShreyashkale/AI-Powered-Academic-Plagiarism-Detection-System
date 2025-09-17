from rest_framework import serializers
from django.utils import timezone
from .models import Assignment, Submission, AssignmentReview
from users.serializers import UserSerializer  # nested student info

# Config
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
VALID_EXTENSIONS = [".pdf", ".txt", ".doc", ".docx"]  # 🔥 allow both PDF/TXT & DOC/DOCX to match professor.html


class AssignmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    professor_username = serializers.CharField(source="professor.username", read_only=True)

    class Meta:
        model = Assignment
        fields = "__all__"
        read_only_fields = ["professor", "created_at"]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file:
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None

    def validate_deadline(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("Deadline must be in the future.")
        return value


class SubmissionSerializer(serializers.ModelSerializer):
    document_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Submission
        fields = "__all__"
        read_only_fields = ["student", "uploaded_at", "similarity_score", "status", "document_url"]

    def get_document_url(self, obj):
        request = self.context.get("request")
        if not obj.document:
            return None
        return request.build_absolute_uri(obj.document.url) if request else obj.document.url

    def validate(self, attrs):
        file = attrs.get("document") or self.initial_data.get("document")
        if file:
            import os
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in VALID_EXTENSIONS:
                raise serializers.ValidationError(f"Invalid file type. Allowed: {', '.join(VALID_EXTENSIONS)}")
            if file.size > MAX_UPLOAD_SIZE:
                raise serializers.ValidationError("File size exceeds 10MB limit.")
        return super().validate(attrs)


class SubmissionDetailSerializer(serializers.ModelSerializer):
    assignment = AssignmentSerializer(read_only=True)
    student = UserSerializer(read_only=True)
    document_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Submission
        fields = "__all__"

    def get_document_url(self, obj):
        request = self.context.get("request")
        if obj.document:
            return request.build_absolute_uri(obj.document.url) if request else obj.document.url
        return None


class AssignmentReviewSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source="student.username", read_only=True)

    class Meta:
        model = AssignmentReview
        fields = ["id", "assignment", "student", "student_username", "comment", "created_at"]
        read_only_fields = ["student", "created_at"]
