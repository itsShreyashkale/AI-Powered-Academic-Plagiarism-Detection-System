"""
URL configuration for plagiarism_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# plagiarism_project/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.shortcuts import render, redirect

# --- Simple page render helpers ---
def root_redirect(request): return redirect("login_page")
def login_page(request): return render(request, "login.html")
def logout_page(request): return render(request, "logout.html")
def register_page(request): return render(request, "register.html")
def dashboard_page(request): return render(request, "dashboard.html")
def profile_page(request): return render(request, "profile.html")

# Role-based dashboards
def student_page(request): return render(request, "student.html")
def professor_page(request): return render(request, "professor.html")

# Plagiarism dashboard
def plagiarism_dashboard_page(request): return render(request, "plagiarism.html")

# --- Swagger / API Docs ---
schema_view = get_schema_view(
    openapi.Info(
        title="Plagiarism Detection API",
        default_version="v1",
        description="API documentation for AI-Powered Academic Plagiarism Detection System",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # ✅ Root redirect → login
    path("", root_redirect, name="root_redirect"),

    # ✅ Frontend pages
    path("login/", login_page, name="login_page"),
    path("logout/", logout_page, name="logout_page"),
    path("register/", register_page, name="register_page"),
    path("dashboard/", dashboard_page, name="dashboard_page"),
    path("profile/", profile_page, name="profile_page"),

    # ✅ Role-based dashboards
    path("student/", student_page, name="student_dashboard"),
    path("professor/", professor_page, name="professor_dashboard"),

    # ✅ Plagiarism
    path("plagiarism/", plagiarism_dashboard_page, name="plagiarism_dashboard_page"),

    # ✅ API endpoints
    path("api/users/", include("users.urls")),
    path("api/documents/", include("documents.urls")),
    path("api/plagiarism/", include("plagiarism.urls")),

    # ✅ API docs (Swagger / ReDoc)
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
