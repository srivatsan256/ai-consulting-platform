"""
Workflow runtime services.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from workflows.models import WorkflowHistory

if TYPE_CHECKING:
    from accounts.models import User
    from workflows.models import Workflow, WorkflowExecution, WorkflowStep


def log_workflow_event(
    *,
    workflow: "Workflow",
    execution: Optional["WorkflowExecution"] = None,
    event_type: str = "started",
    message: str = "",
    actor: Optional["User"] = None,
    step: Optional["WorkflowStep"] = None,
    metadata: Optional[dict] = None,
) -> WorkflowHistory:
    """
    Append an immutable event to a workflow's history log.

    ``workflow`` is required so history can be queried per workflow even
    when the event is not tied to a specific execution run.
    """
    return WorkflowHistory.objects.create(
        workflow=workflow,
        workflow_execution=execution,
        event_type=event_type,
        message=message,
        actor=actor,
        step=step,
        metadata=metadata or {},
    )
