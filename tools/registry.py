"""
Centralized Tool Registry for AI Workflow.
Exposes JSON Schemas, tool descriptions, and dispatches executions.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from tools.schemas import RetrieveCaseInput, UpdateTicketInput
from tools.retrieve_case import retrieve_case_details
from tools.update_ticket import update_ticket


class ToolMetadata(BaseModel):
    name: str
    description: str
    is_consequential: bool
    requires_approval: bool
    parameters_schema: Dict[str, Any]


class ToolRegistry:
    """
    Manages typed AI tool definitions and provides JSON schemas for LLM function calling.
    """

    def __init__(self):
        self._tools: Dict[str, ToolMetadata] = {
            "retrieve_case_details": ToolMetadata(
                name="retrieve_case_details",
                description="Retrieve structured details and history of an existing case by its unique integer case_id.",
                is_consequential=False,
                requires_approval=False,
                parameters_schema=RetrieveCaseInput.model_json_schema(),
            ),
            "update_ticket": ToolMetadata(
                name="update_ticket",
                description="Consequential write tool to update ticket/case status. Strictly requires an approved approval_id.",
                is_consequential=True,
                requires_approval=True,
                parameters_schema=UpdateTicketInput.model_json_schema(),
            ),
        }

    def list_tools(self) -> List[ToolMetadata]:
        return list(self._tools.values())

    def get_tool(self, name: str) -> Optional[ToolMetadata]:
        return self._tools.get(name)

    def get_openai_function_definitions(self) -> List[Dict[str, Any]]:
        """Exports tools in standard OpenAI / Anthropic function calling format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters_schema,
                },
            }
            for t in self._tools.values()
        ]


tool_registry = ToolRegistry()
