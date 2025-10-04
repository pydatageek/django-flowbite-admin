from django.contrib import admin
from django.urls import path

from .admin import project_admin_site

urlpatterns = [
    path("admin/", admin.site.urls),
    path("project-admin/", project_admin_site.urls),
]
