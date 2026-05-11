"""Django forms for user registration with Swiss address autocomplete."""

from django import forms

from postal_address import PostalAddressClient, PostalAddressError

from .models import User


class UserRegistrationForm(forms.ModelForm):
    """Registration form with Swiss address autocomplete."""

    address = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control autocomplete-input",
                "placeholder": "Start typing street (e.g. Bahnhofstrasse)",
                "autocomplete": "off",
                "data-toggle": "street-autocomplete",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "house_number", "postal_code", "city"]
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email address",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "First name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Last name",
                }
            ),
            "house_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "House number",
                }
            ),
            "postal_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Postal code",
                    "autocomplete": "off",
                    "data-toggle": "zip-autocomplete",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "City",
                    "autocomplete": "off",
                    "data-toggle": "city-autocomplete",
                }
            ),
        }

    def clean(self) -> dict[str, object]:
        """Validate full Swiss address on register submit."""
        cleaned_data = super().clean()

        street = str(cleaned_data.get("address", "")).strip()
        house_number = str(cleaned_data.get("house_number", "")).strip() or None
        postal_code = str(cleaned_data.get("postal_code", "")).strip()
        city = str(cleaned_data.get("city", "")).strip()

        if not street or not postal_code or not city:
            return cleaned_data

        try:
            client = PostalAddressClient(country="ch")
            result = client.validate_address(
                street=street,
                house_number=house_number,
                zip_code=postal_code,
                city=city,
            )
            if not isinstance(result, dict):
                raise forms.ValidationError("Address could not be validated.")

            # Keep normalized values for persistence.
            cleaned_data["address"] = result.get("Street", street)
            cleaned_data["postal_code"] = result.get("PostalCode", postal_code)
            cleaned_data["city"] = result.get("City", city)
        except PostalAddressError as exc:
            raise forms.ValidationError(f"Address validation error: {exc}") from exc

        return cleaned_data
