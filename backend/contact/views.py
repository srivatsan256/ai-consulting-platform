import logging

from django.conf import settings
from django.core.mail import send_mail

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ContactMessageSerializer

logger = logging.getLogger(__name__)


class ContactSubmitAPIView(APIView):
    """Public endpoint for the marketing contact form."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.save(
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:512],
        )

        self._notify(message)

        return Response(
            {
                "message": "Your message has been received. Our team will get back to you within one business day.",
                "id": message.id,
            },
            status=status.HTTP_201_CREATED,
        )

    def _notify(self, message):
        try:
            send_mail(
                subject=f"[Contact] {message.inquiry_type} — {message.first_name} {message.last_name}",
                message=(
                    f"From: {message.first_name} {message.last_name} "
                    f"<{message.email}>\n"
                    f"Inquiry Type: {message.inquiry_type}\n"
                    f"IP: {message.ip_address or 'unknown'}\n\n"
                    f"{message.message}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_NOTIFY_EMAIL]
                if getattr(settings, "CONTACT_NOTIFY_EMAIL", None)
                else [],
            )
        except Exception:
            logger.exception("Failed to send contact notification email for message #%s", message.id)
