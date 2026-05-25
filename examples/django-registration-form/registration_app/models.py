"""Django models for user registration with Swiss address fields."""

from django.db import models


class User(models.Model):
    """User model with Swiss address fields."""

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    street = models.CharField(max_length=255, blank=True)
    house_number = models.CharField(max_length=10, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """Return the user's full name followed by their email in parentheses."""
        return f"{self.first_name} {self.last_name} ({self.email})"

    class Meta:
        """Meta options for the User model."""

        verbose_name = "User"
        verbose_name_plural = "Users"
