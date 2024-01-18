"""
URL configuration for main project.

"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # API
    path("api/v1/", include("apps.game.api.v1.urls")),
]
