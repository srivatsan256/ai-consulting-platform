from django.db import models


class ContactMessage(models.Model):

    INQUIRY_TYPE = [
        ("sales", "Sales & Integration"),
        ("support", "Technical Support"),
        ("partnership", "Partnership"),
        ("other", "Other"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    inquiry_type = models.CharField(max_length=50, choices=INQUIRY_TYPE, default="other")
    message = models.TextField()

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)

    is_handled = models.BooleanField(default=False)
    handled_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"
