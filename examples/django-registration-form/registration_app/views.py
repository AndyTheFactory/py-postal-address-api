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


def _merge_unique(values: list[str]) -> list[str]:
    """Return values with duplicates removed while preserving order."""
    seen: set[str] = set()
    merged: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        merged.append(value)
    return merged


def _context_query(street: str | None = None, zip_code: str | None = None, city: str | None = None) -> str:
    """Build an unstructured query from available address parts."""
    parts = [street, zip_code, city]
    return " ".join(part.strip() for part in parts if part and part.strip())


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
                suggestions.append(
                    {
                        "label": item.Street,
                        "value": item.Street,
                        "postal_code": item.Zipcode,
                        "city": item.City,
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
    street = request.GET.get("street", "").strip() or None

    if not query or len(query) < 1:
        return JsonResponse({"results": []})

    try:
        api_key = os.getenv("RAPIDAPI_KEY")
        if not api_key:
            return JsonResponse({"error": "API key not configured"}, status=500)

        client = PostalAddressClient(country="ch", api_key=api_key)
        zip_matches = client.get_zip_list(zip_prefix=query, city=city)

        contextual_zip_matches: list[str] = []
        if street:
            contextual_results = client.autocomplete(_context_query(street=street, zip_code=query, city=city))
            contextual_zip_matches = [
                item.Zipcode for item in contextual_results if item.Zipcode and item.Zipcode.startswith(query)
            ]

        results = _merge_unique(contextual_zip_matches + zip_matches)

        suggestions = [{"label": item, "value": item} for item in results[:10]]

        return JsonResponse({"results": suggestions})
    except PostalAddressError as exc:
        return JsonResponse({"error": str(exc)}, status=400)


@require_http_methods(["GET"])
def autocomplete_swiss_city(request: HttpRequest) -> JsonResponse:
    """City autocomplete endpoint."""
    query = request.GET.get("q", "").strip()
    zip_code = request.GET.get("zip", "").strip() or None
    street = request.GET.get("street", "").strip() or None

    if not query or len(query) < 1:
        return JsonResponse({"results": []})

    try:
        api_key = os.getenv("RAPIDAPI_KEY")
        if not api_key:
            return JsonResponse({"error": "API key not configured"}, status=500)

        client = PostalAddressClient(country="ch", api_key=api_key)
        city_matches = client.get_city_list(city=query, zip_code=zip_code)

        contextual_city_matches: list[str] = []
        if street:
            contextual_results = client.autocomplete(_context_query(street=street, zip_code=zip_code, city=query))
            contextual_city_matches = [
                item.City for item in contextual_results if item.City and item.City.lower().startswith(query.lower())
            ]

        results = _merge_unique(contextual_city_matches + city_matches)

        suggestions: list[dict[str, str]] = []
        if isinstance(results, list):
            for item in results[:10]:
                suggestions.append(
                    {
                        "label": str(item),
                        "value": str(item),
                        "postal_code": zip_code or "",
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

    min_length = 1 if (zip_code or city) else 2
    if not query or len(query) < min_length:
        return JsonResponse({"results": []})

    try:
        api_key = os.getenv("RAPIDAPI_KEY")
        if not api_key:
            return JsonResponse({"error": "API key not configured"}, status=500)

        client = PostalAddressClient(country="ch", api_key=api_key)
        results = client.get_street_list(street=query, zip_code=zip_code, city=city)

        if not results and (zip_code or city):
            contextual_results = client.autocomplete(_context_query(street=query, zip_code=zip_code, city=city))
            results = _merge_unique(
                [
                    item.Street
                    for item in contextual_results
                    if item.Street and item.Street.lower().startswith(query.lower())
                ]
            )

        suggestions: list[dict[str, str]] = []
        if isinstance(results, list):
            for item in results[:10]:
                street = str(item)
                suggestions.append(
                    {
                        "label": street,
                        "value": street,
                        "postal_code": zip_code or "",
                        "city": city or "",
                    }
                )

        return JsonResponse({"results": suggestions})
    except PostalAddressError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
