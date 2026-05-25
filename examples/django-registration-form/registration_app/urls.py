"""URL routing for Django registration example."""

from django.urls import path

from .views import (
    RegistrationSuccessView,
    UserRegistrationView,
    autocomplete_swiss_address,
    autocomplete_swiss_city,
    autocomplete_swiss_street,
    autocomplete_swiss_zip,
)

urlpatterns = [
    path("", UserRegistrationView.as_view(), name="register"),
    path("register/", UserRegistrationView.as_view(), name="register_alias"),
    path("registration-success/", RegistrationSuccessView.as_view(), name="registration_success"),
    path("api/ch-address/autocomplete/", autocomplete_swiss_address, name="ch_autocomplete"),
    path("api/ch-address/autocomplete-zip/", autocomplete_swiss_zip, name="ch_autocomplete_zip"),
    path("api/ch-address/autocomplete-city/", autocomplete_swiss_city, name="ch_autocomplete_city"),
    path(
        "api/ch-address/autocomplete-street/",
        autocomplete_swiss_street,
        name="ch_autocomplete_street",
    ),
]
