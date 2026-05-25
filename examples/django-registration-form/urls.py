"""URL routing for Django registration example."""

from django.urls import path

from .views import UserRegistrationView, autocomplete_swiss_address

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("api/ch-address/autocomplete/", autocomplete_swiss_address, name="ch_autocomplete"),
]
