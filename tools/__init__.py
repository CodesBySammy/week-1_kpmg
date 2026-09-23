"""
Tools Subsystem for Week 4 Controlled AI Workflows.
Implements typed AI tools with JSON schemas, deterministic errors, and idempotency.
"""

from .schemas import (
    RetrieveCaseInput,
    RetrieveCaseOutput,
    UpdateTicketInput,
    UpdateTicketOutput,
    ToolError,
)
from .retrieve_case import retrieve_case_details
from .update_ticket import update_ticket
from .registry import ToolRegistry, tool_registry

__all__ = [
    "RetrieveCaseInput",
    "RetrieveCaseOutput",
    "UpdateTicketInput",
    "UpdateTicketOutput",
    "ToolError",
    "retrieve_case_details",
    "update_ticket",
    "ToolRegistry",
    "tool_registry",
]
