from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Assignment(models.Model):
    professor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="assignments/", blank=True, null=True)

    def __str__(self):
        return self.title


class Submission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions")
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    document = models.FileField(upload_to="submissions/")   # file upload
    uploaded_at = models.DateTimeField(auto_now_add=True)
    similarity_score = models.FloatField(default=0.0)       # filled by plagiarism app
    status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return f"{self.student} → {self.assignment}"


class AssignmentReview(models.Model):
    assignment = models.ForeignKey("Assignment", on_delete=models.CASCADE, related_name="reviews")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assignment_reviews")
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.student.username} on {self.assignment.title}"
