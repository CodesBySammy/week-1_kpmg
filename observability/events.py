"""
Structured Domain Lifecycle Events for Observability and Auditing.
"""
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
import json
import logging
from pydantic import BaseModel, Field

logger = logging.getLogger("workflow.events")


class EventType(str, Enum):
    REQUEST_RECEIVED = "request_received"
    INTENT_DETECTED = "intent_detected"
    TOOL_PROPOSED = "tool_proposed"
    AUTHORIZATION_CHECKED = "authorization_checked"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_REJECTED = "approval_rejected"
    TOOL_STARTED = "tool_started"
    TOOL_COMPLETED = "tool_completed"
    TOOL_FAILED = "tool_failed"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"


class WorkflowEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    event_type: EventType
    correlation_id: str
    request_id: Optional[str] = None
    username: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    payload: Dict[str, Any] = Field(default_factory=dict)


class EventLogger:
    """Thread-safe collector preserving recent structured events for auditing."""

    MAX_HISTORY = 1000

    def __init__(self):
        self._events: List[WorkflowEvent] = []

    def record(
        self,
        event_type: EventType,
        correlation_id: str,
        request_id: Optional[str] = None,
        username: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> WorkflowEvent:
        event = WorkflowEvent(
            event_type=event_type,
            correlation_id=correlation_id,
            request_id=request_id,
            username=username,
            payload=payload or {},
        )
        self._events.append(event)
        if len(self._events) > self.MAX_HISTORY:
            self._events.pop(0)

        # Log as structured JSON
        logger.info(
            f"Event: {event.event_type.value}",
            extra={"structured_event": event.model_dump()},
        )
        return event

    def get_events_for_correlation(self, correlation_id: str) -> List[WorkflowEvent]:
        return [e for e in self._events if e.correlation_id == correlation_id]

    def list_recent(self, limit: int = 50) -> List[WorkflowEvent]:
        return self._events[-limit:]


event_logger = EventLogger()
