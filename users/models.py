from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
        ROLE_CHOICES = (
        ('student', 'Student'),
        ('professor', 'Professor'),
        ('admin', 'Admin'),
        )
        
        role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
        
        def __str__(self):
                return f"{self.username} ({self.role})"