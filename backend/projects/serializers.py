from rest_framework import serializers
from .models import Project, Document, VerificationReport


class DocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        request = self.context.get("request") if hasattr(self, "context") else None
        try:
            url = obj.file.url
        except Exception:
            return ""
        if request is not None:
            return request.build_absolute_uri(url)
        return url

    class Meta:
        model = Document
        fields = [
            "id",
            "project",
            "doc_type",
            "level",
            "file",
            "file_url",
            "extracted_text",
            "verification_status",
            "missing_keywords",
            "missing_sections",
            "uploaded_at",
        ]
        read_only_fields = (
            "id",
            "project",
            "level",
            "extracted_text",
            "verification_status",
            "missing_keywords",
            "missing_sections",
            "uploaded_at",
        )


class VerificationReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationReport
        fields = ["id", "project", "report_data", "summary", "generated_at"]
        read_only_fields = fields


class ProjectSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)
    verification_report = VerificationReportSerializer(read_only=True)

    class Meta:
        model = Project
        fields = "__all__"
