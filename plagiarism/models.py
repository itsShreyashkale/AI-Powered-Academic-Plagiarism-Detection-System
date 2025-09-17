from django.db import models

# Create your models here.
from documents.models import Submission

class PlagiarismResult(models.Model):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name="plagiarism_result")
    similarity_score = models.FloatField()
    compared_with = models.TextField(blank=True, null=True)   # list of compared submission IDs
    algorithm = models.CharField(max_length=50, default="TF-IDF")
    report = models.JSONField(blank=True, null=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    @property
    def plagiarism_level(self):
        if self.similarity_score >= 70:
            return "High"
        elif self.similarity_score >= 40:
            return "Moderate"
        else:
            return "Low"
    
    
    def __str__(self):
        return f"Plagiarism Result for Submission {self.submission.id}"
