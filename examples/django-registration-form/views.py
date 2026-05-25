"""Django views for user registration with Swiss address autocomplete."""

import os

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView

from postal_address import PostalAddressClient, PostalAddressError

from .forms import UserRegistrationForm
from .models import User


class UserRegistrationView(CreateView):
    """View for user registration with Swiss address validation."""

    model = User
    form_class = UserRegistrationForm
    template_name = "registration_form.html"
    success_url = "/registration-success/"

    def form_valid(self, form):
        """Save user with validated Swiss address."""
        user = form.save(commit=False)

        try:
            client = PostalAddressClient(country="ch")
            validation = client.validate_address(
                street=form.cleaned_data.get("address"),
                zip_code=form.cleaned_data.get("postal_code"),
                city=form.cleaned_data.get("city"),
            )
            if validation:
                user.street = validation.Street or form.cleaned_data.get("address")
                user.postal_code = validation.Zipcode or form.cleaned_data.get("postal_code")
                user.city = validation.City or form.cleaned_data.get("city")
        except PostalAddressError:
            pass

        user.save()
        return super().form_valid(form)


@require_http_methods(["GET"])
def autocomplete_swiss_address(request):
    """API endpoint for Swiss address autocomplete via AJAX.

    Query param: q (search query)
    Returns: JSON list of matching addresses
    """
    query = request.GET.get("q", "").strip()

    if not query or len(query) < 2:
        return JsonResponse({"results": []})

    try:
        api_key = os.getenv("RAPIDAPI_KEY")
        if not api_key:
            return JsonResponse(
                {"error": "API key not configured"},
                status=500,
            )

        client = PostalAddressClient(country="ch", api_key=api_key)
        results = client.autocomplete(query)

        # Transform results for frontend autocomplete widget
        suggestions = []
        if isinstance(results, list):
            for item in results[:10]:  # Limit to 10 suggestions
                suggestion = {
                    "label": item.Street,
                    "value": item.Street,
                    "postal_code": item.Zipcode,
                    "city": item.City,
                }
                suggestions.append(suggestion)

        return JsonResponse({"results": suggestions})

    except PostalAddressError as exc:
        return JsonResponse(
            {"error": str(exc)},
            status=400,
        )
