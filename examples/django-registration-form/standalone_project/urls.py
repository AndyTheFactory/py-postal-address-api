"""Root URL configuration for standalone Django example."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("registration_app.urls")),
]
