"""Application configuration for the registration_app Django application.

This module defines the AppConfig subclass used by Django to configure
the registration_app application (registration forms and related views).
"""

from django.apps import AppConfig


class RegistrationAppConfig(AppConfig):
    """Django AppConfig for the registration_app.

    Sets the default auto field for models and the application name.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "registration_app"
