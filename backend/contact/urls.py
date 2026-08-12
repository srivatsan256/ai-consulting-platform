from django.urls import path

from .views import ContactSubmitAPIView

urlpatterns = [
    path("", ContactSubmitAPIView.as_view(), name="contact-submit"),
]
