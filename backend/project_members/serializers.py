from rest_framework import serializers
from .models import ProjectMember


class ProjectMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectMember
        fields = "__all__"