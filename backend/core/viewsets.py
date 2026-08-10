from rest_framework import viewsets, status
from rest_framework.response import Response

from core.logging import log_info, log_error
from core.mixins import CompanyQuerySetMixin
from core.pagination import StandardPagination
from core.responses import success_response, created_response, error_response


class BaseTenantViewSet(CompanyQuerySetMixin, viewsets.ModelViewSet):
    """
    Reusable ViewSet with search, ordering, pagination, company isolation,
    standard responses, audit integration, and logging.
    """

    pagination_class = StandardPagination
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    search_fields = ["name"]

    def list(self, request, *args, **kwargs):
        log_info(f"Listing {self.__class__.__name__}", extra={"user": request.user.pk})
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        log_info(f"Creating {self.__class__.__name__}", extra={"user": request.user.pk})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return created_response(
            data=serializer.data,
            message=f"{self.__class__.__name__} created successfully.",
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)

    def update(self, request, *args, **kwargs):
        log_info(f"Updating {self.__class__.__name__}", extra={"user": request.user.pk})
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(
            data=serializer.data,
            message=f"{self.__class__.__name__} updated successfully.",
        )

    def destroy(self, request, *args, **kwargs):
        log_info(f"Deleting {self.__class__.__name__}", extra={"user": request.user.pk})
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(message=f"{self.__class__.__name__} deleted successfully.")

    def perform_destroy(self, instance):
        """
        Soft-delete when the model supports it; otherwise hard-delete.
        """
        if hasattr(instance, "soft_delete"):
            instance.soft_delete(user=getattr(self.request, "user", None))
            return
        if hasattr(instance, "is_deleted"):
            from django.utils import timezone

            instance.is_deleted = True
            if hasattr(instance, "deleted_at"):
                instance.deleted_at = timezone.now()
            instance.save()
            return
        instance.delete()
