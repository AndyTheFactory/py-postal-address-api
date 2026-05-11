"""Django views for user registration with Swiss address autocomplete."""

from __future__ import annotations

import os

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, TemplateView

from postal_address import PostalAddressClient, PostalAddressError

from .forms import UserRegistrationForm
from .models import User


class UserRegistrationView(CreateView):
    """View for user registration with Swiss address validation."""

    model = User
    form_class = UserRegistrationForm
    template_name = "registration_app/registration_form.html"
    success_url = reverse_lazy("registration_success")

    def form_valid(self, form: UserRegistrationForm) -> HttpResponse:
        """Save user with already-validated Swiss address fields."""
        user = form.save(commit=False)
        user.street = str(form.cleaned_data.get("address", ""))
        user.postal_code = str(form.cleaned_data.get("postal_code", ""))
        user.city = str(form.cleaned_data.get("city", ""))

        user.save()
        self.object = user
        return super().form_valid(form)


class RegistrationSuccessView(TemplateView):
    template_name = "registration_app/registration_success.html"


@require_http_methods(["GET"])
def autocomplete_swiss_address(request: HttpRequest) -> JsonResponse:
    """API endpoint for Swiss address autocomplete via AJAX."""
    query = request.GET.get("q", "").strip()

    if not query or len(query) < 2:
        return JsonResponse({"results": []})

    try:
        api_key = os.getenv("RAPIDAPI_KEY")
        if not api_key:
            return JsonResponse({"error": "API key not configured"}, status=500)

        client = PostalAddressClient(country="ch", api_key=api_key)
        results = client.autocomplete(query)

        suggestions: list[dict[str, str]] = []
        if isinstance(results, list):
            for item in results[:10]:
                if isinstance(item, dict):
                    suggestions.append(
                        {
                            "label": item.get("Street") or str(item),
                            "value": item.get("Street") or str(item),
                            "postal_code": item.get("PostalCode", ""),
                            "city": item.get("City", ""),
                        }
                    )

        return JsonResponse({"results": suggestions})

    except PostalAddressError as exc:
        return JsonResponse({"error": str(exc)}, status=400)


@require_http_methods(["GET"])
def autocomplete_swiss_zip(request: HttpRequest) -> JsonResponse:
    """ZIP autocomplete endpoint."""
    query = request.GET.get("q", "").strip()
    city = request.GET.get("city", "").strip() or None

    if not query or len(query) < 1:
        return JsonResponse({"results": []})

    try:
        api_key = os.getenv("RAPIDAPI_KEY")
        if not api_key:
            return JsonResponse({"error": "API key not configured"}, status=500)

        client = PostalAddressClient(country="ch", api_key=api_key)
        results = client.get_zip_list(zip_prefix=query, city=city)

        suggestions = [{"label": item, "value": item} for item in results[:10]]

        return JsonResponse({"results": suggestions})
    except PostalAddressError as exc:
        return JsonResponse({"error": str(exc)}, status=400)


@require_http_methods(["GET"])
def autocomplete_swiss_city(request: HttpRequest) -> JsonResponse:
    """City autocomplete endpoint."""
    query = request.GET.get("q", "").strip()
    zip_code = request.GET.get("zip", "").strip() or None

    if not query or len(query) < 1:
        return JsonResponse({"results": []})

    try:
        api_key = os.getenv("RAPIDAPI_KEY")
        if not api_key:
            return JsonResponse({"error": "API key not configured"}, status=500)

        client = PostalAddressClient(country="ch", api_key=api_key)
        results = client.get_city_list(city=query, zip_code=zip_code)

        suggestions: list[dict[str, str]] = []
        if isinstance(results, list):
            for item in results[:10]:
                if isinstance(item, dict):
                    suggestions.append(
                        {
                            "label": item.get("City") or str(item),
                            "value": item.get("City") or str(item),
                            "postal_code": item.get("PostalCode", ""),
                        }
                    )

        return JsonResponse({"results": suggestions})
    except PostalAddressError as exc:
        return JsonResponse({"error": str(exc)}, status=400)


@require_http_methods(["GET"])
def autocomplete_swiss_street(request: HttpRequest) -> JsonResponse:
    """Street autocomplete narrowed by ZIP and city."""
    query = request.GET.get("q", "").strip()
    zip_code = request.GET.get("zip", "").strip() or None
    city = request.GET.get("city", "").strip() or None

    if not query or len(query) < 2:
        return JsonResponse({"results": []})

    try:
        api_key = os.getenv("RAPIDAPI_KEY")
        if not api_key:
            return JsonResponse({"error": "API key not configured"}, status=500)

        client = PostalAddressClient(country="ch", api_key=api_key)
        results = client.get_street_list(street=query, zip_code=zip_code, city=city)

        suggestions: list[dict[str, str]] = []
        if isinstance(results, list):
            for item in results[:10]:
                if isinstance(item, dict):
                    street = item.get("Street") or str(item)
                    suggestions.append(
                        {
                            "label": street,
                            "value": street,
                            "postal_code": item.get("PostalCode", zip_code or ""),
                            "city": item.get("City", city or ""),
                        }
                    )

        return JsonResponse({"results": suggestions})
    except PostalAddressError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
