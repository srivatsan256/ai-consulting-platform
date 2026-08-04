from django.db import models


class Company(models.Model):
    company_name = models.CharField(max_length=255, unique=True)
    industry = models.CharField(max_length=150)
    business_description = models.TextField(blank=True)

    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "companies"
        ordering = ["company_name"]

    def __str__(self):
        return self.company_name
