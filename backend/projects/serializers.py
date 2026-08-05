from django.utils import timezone
from rest_framework import serializers

from .models import Project, ProjectPhase, Milestone, LevelModule, ProjectDocument


# The frontend uses uppercase pipeline statuses while the backend uses
# lowercase lifecycle statuses. Translate between the two so the existing
# UI keeps working without losing data fidelity.
FRONTEND_STATUS_MAP = {
    "planning": "DISCOVERY",
    "discovery": "DISCOVERY",
    "development": "PROCESSING",
    "testing": "VERIFICATION",
    "deployment": "REVIEW",
    "completed": "COMPLETED",
    "on_hold": "ON_HOLD",
}

BACKEND_STATUS_MAP = {
    "DISCOVERY": "discovery",
    "VERIFICATION": "testing",
    "PROCESSING": "development",
    "REVIEW": "deployment",
    "COMPLETED": "completed",
    "ON_HOLD": "on_hold",
    "PLANNING": "planning",
}


class ProjectDocumentSerializer(serializers.ModelSerializer):

    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ProjectDocument
        fields = [
            "id",
            "file",
            "file_url",
            "original_name",
            "doc_type",
            "level",
            "verification_status",
            "verification_score",
            "missing_requirements",
            "uploaded_at",
        ]
        read_only_fields = fields

    def get_file_url(self, obj) -> str | None:
        if not obj.file:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url


class LevelModuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = LevelModule
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):

    company_name = serializers.CharField(
        source="company.company_name",
        read_only=True,
    )

    project_manager_name = serializers.SerializerMethodField()

    documents = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "project_name",
            "company",
            "company_name",
            "project_manager",
            "project_manager_name",
            "description",
            "industry",
            "team_members",
            "objectives",
            "expected_timeline",
            "start_date",
            "end_date",
            "status",
            "priority",
            "progress",
            "current_level",
            "completed_levels",
            "level_scores",
            "readiness_score",
            "verification_report",
            "documents",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")

    def get_project_manager_name(self, obj) -> str | None:
        if obj.project_manager:
            return obj.project_manager.get_full_name() or obj.project_manager.username
        return None

    def get_documents(self, obj) -> list:
        return ProjectDocumentSerializer(
            obj.uploaded_documents.all(),
            many=True,
            context=self.context,
        ).data

    def get_fields(self):
        fields = super().get_fields()
        # Company and start date are inferred on create from the request
        # user's membership, so the frontend does not need to send them.
        fields["company"].required = False
        fields["start_date"].required = False
        return fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        status = data.get("status")
        data["status"] = FRONTEND_STATUS_MAP.get(status, status)
        return data

    def to_internal_value(self, data):
        if isinstance(data, dict) and data.get("status"):
            data["status"] = BACKEND_STATUS_MAP.get(
                str(data["status"]).upper(),
                str(data["status"]),
            )
        return super().to_internal_value(data)

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        company = None

        if user and user.is_authenticated:
            from company_members.models import CompanyMember

            membership = CompanyMember.objects.primary_for_user(user)
            if membership:
                company = membership.company

        if company is None:
            raise serializers.ValidationError(
                {"company": "No company associated with this user."}
            )

        validated_data["company"] = company
        validated_data.setdefault("project_manager", user if user else None)
        if not validated_data.get("start_date"):
            validated_data["start_date"] = timezone.localdate()

        return super().create(validated_data)


class ProjectPhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPhase
        fields = "__all__"


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = "__all__"
