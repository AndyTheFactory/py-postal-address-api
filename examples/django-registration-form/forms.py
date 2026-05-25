"""Django forms for user registration with Swiss address autocomplete."""

from django import forms

from postal_address import PostalAddressClient, PostalAddressError


class SwissAddressField(forms.CharField):
    """Custom form field for Swiss addresses with validation."""

    def clean(self, value: str) -> str:
        """Validate address exists via API."""
        if not value:
            return value

        try:
            client = PostalAddressClient(country="ch")
            results = client.autocomplete(value)
            if not results:
                raise forms.ValidationError("Address not found. Please check and try again.")
        except PostalAddressError as exc:
            raise forms.ValidationError(f"Address validation error: {exc}") from exc

        return value


class UserRegistrationForm(forms.Form):
    """Registration form with Swiss address autocomplete."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Email address",
            }
        ),
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "First name",
            }
        ),
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Last name",
            }
        ),
    )
    address = SwissAddressField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control autocomplete-input",
                "placeholder": "Start typing Swiss address (e.g. Bahnhofstrasse Zurich)",
                "autocomplete": "off",
                "data-toggle": "autocomplete",
            }
        ),
    )
    postal_code = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Postal code",
                "readonly": True,
            }
        ),
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "City",
                "readonly": True,
            }
        ),
    )
