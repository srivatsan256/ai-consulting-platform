from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Company
from .serializers import CompanySerializer
from .filters import CompanyFilter


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    filterset_class = CompanyFilter
    search_fields = ["company_name", "industry"]
    ordering_fields = ["company_name", "created_at"]
    ordering = ["company_name"]
