from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from core.prompt_manager import list_prompts, get_prompt, render_prompt


@extend_schema(
    summary="List all available prompt templates",
    responses={
        200: inline_serializer(
            name="PromptListItem",
            fields={
                "key": serializers.CharField(),
                "name": serializers.CharField(),
                "description": serializers.CharField(),
            },
            many=True,
        )
    },
    tags=["prompts"],
    operation_id="ai_engine_prompts_list",
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def prompt_list(request):
    prompts = list_prompts()
    return Response(prompts)


@extend_schema(
    summary="Get prompt template details",
    responses={
        200: inline_serializer(
            name="PromptDetailResponse",
            fields={
                "key": serializers.CharField(),
                "name": serializers.CharField(),
                "description": serializers.CharField(),
                "system_prompt": serializers.CharField(),
                "user_prompt_template": serializers.CharField(),
                "temperature": serializers.FloatField(),
                "max_tokens": serializers.IntegerField(),
            }
        ),
        404: inline_serializer(name="PromptErrorResponse", fields={"error": serializers.CharField()})
    },
    tags=["prompts"],
    operation_id="ai_engine_prompts_detail",
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def prompt_detail(request, template_name):
    prompt = get_prompt(template_name)
    if not prompt:
        return Response(
            {"error": "Prompt template not found."},
            status=404,
        )
    return Response({
        "key": template_name,
        "name": prompt["name"],
        "description": prompt["description"],
        "system_prompt": prompt["system_prompt"],
        "user_prompt_template": prompt["user_prompt"],
        "temperature": prompt.get("temperature", 0.5),
        "max_tokens": prompt.get("max_tokens", 1500),
    })


@extend_schema(
    summary="Preview rendered prompt with variables",
    request=inline_serializer(
        name="PromptPreviewRequest",
        fields={"variables": serializers.DictField(required=False)}
    ),
    responses={
        200: inline_serializer(
            name="PromptPreviewResponse",
            fields={
                "system_prompt": serializers.CharField(),
                "user_prompt": serializers.CharField(),
            }
        ),
        400: inline_serializer(name="PromptPreviewErrorResponse", fields={"error": serializers.CharField()})
    },
    tags=["prompts"],
    operation_id="ai_engine_prompts_preview",
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def prompt_preview(request, template_name):
    kwargs = request.data.get("variables", {})
    try:
        rendered = render_prompt(template_name, **kwargs)
        return Response(rendered)
    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=400,
        )
