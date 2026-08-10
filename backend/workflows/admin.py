from django.contrib import admin

from .models import Workflow, WorkflowHistory, WorkflowStep, WorkflowExecution


class WorkflowStepInline(admin.TabularInline):
    model = WorkflowStep
    extra = 0


class WorkflowHistoryInline(admin.TabularInline):
    model = WorkflowHistory
    extra = 0
    fields = ("event_type", "actor", "message", "created_at")
    readonly_fields = ("event_type", "actor", "message", "created_at")


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "project",
        "status",
        "trigger_event",
        "created_by",
        "created_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "name",
        "description",
    )

    inlines = [WorkflowStepInline, WorkflowHistoryInline]


@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):

    list_display = (
        "workflow",
        "name",
        "step_type",
        "order",
    )

    list_filter = (
        "step_type",
    )


@admin.register(WorkflowExecution)
class WorkflowExecutionAdmin(admin.ModelAdmin):

    list_display = (
        "workflow",
        "entity_type",
        "entity_id",
        "status",
        "initiated_by",
        "started_at",
    )

    list_filter = (
        "status",
    )


@admin.register(WorkflowHistory)
class WorkflowHistoryAdmin(admin.ModelAdmin):

    list_display = (
        "workflow",
        "workflow_execution",
        "event_type",
        "actor",
        "step",
        "created_at",
    )

    list_filter = ("event_type",)

    search_fields = ("message",)
