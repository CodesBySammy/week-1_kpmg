"""
Deterministic & Semantic Workflow Router.
Classifies user intent, identifies target tools, extracts arguments,
and flags whether human approval is required.
"""
from enum import Enum
from typing import Dict, Any, Optional, Tuple
import re
from pydantic import BaseModel


class WorkflowIntent(str, Enum):
    RAG_POLICY_QUERY = "RAG_POLICY_QUERY"
    RETRIEVE_CASE_DETAILS = "RETRIEVE_CASE_DETAILS"
    UPDATE_TICKET = "UPDATE_TICKET"
    COMPLIANCE_CASE_CHECK = "COMPLIANCE_CASE_CHECK"
    UNKNOWN = "UNKNOWN"


class WorkflowRoutingDecision(BaseModel):
    intent: WorkflowIntent
    requires_tool: bool
    tool_name: Optional[str] = None
    tool_arguments: Dict[str, Any] = {}
    requires_approval: bool = False
    reasoning: str


class WorkflowRouter:
    """
    Routes user requests safely between pure policy RAG,
    case retrieval read tools, and approval-gated ticket write tools.
    """

    # Status synonyms
    STATUS_MAP = {
        "resolve": "resolved",
        "resolved": "resolved",
        "close": "closed",
        "closed": "closed",
        "open": "open",
        "reopen": "open",
        "in_progress": "in_progress",
        "in progress": "in_progress",
        "progress": "in_progress",
    }

    @classmethod
    def route(cls, query: str) -> WorkflowRoutingDecision:
        q_lower = query.lower().strip()

        # 1. Check for UPDATE TICKET (Consequential Write Intent)
        update_match = re.search(
            r"(?:update|change|set|mark|transition)\s+(?:ticket|case)\s+#?(\d+)\s+(?:status\s+)?(?:to|as)?\s*([a-zA-Z_]+)",
            q_lower,
        )
        if update_match:
            ticket_id = int(update_match.group(1))
            raw_status = update_match.group(2).lower()
            norm_status = cls.STATUS_MAP.get(raw_status, raw_status)

            return WorkflowRoutingDecision(
                intent=WorkflowIntent.UPDATE_TICKET,
                requires_tool=True,
                tool_name="update_ticket",
                tool_arguments={
                    "ticket_id": ticket_id,
                    "status": norm_status,
                    "comment": f"Requested status change to '{norm_status}' via AI Workflow.",
                },
                requires_approval=True,  # Mandatory human approval for write actions
                reasoning="Detected ticket update intent. Write operation requires human approval gate.",
            )

        # 2. Check for RETRIEVE CASE DETAILS (Safe Read Intent)
        case_read_match = re.search(
            r"(?:get|fetch|retrieve|show|find|view|details\s+for|info\s+on)\s+(?:case|ticket)\s+#?(\d+)",
            q_lower,
        ) or re.search(r"(?:case|ticket)\s+#?(\d+)\s+details", q_lower)
        if case_read_match:
            case_id = int(case_read_match.group(1))
            return WorkflowRoutingDecision(
                intent=WorkflowIntent.RETRIEVE_CASE_DETAILS,
                requires_tool=True,
                tool_name="retrieve_case_details",
                tool_arguments={"case_id": case_id},
                requires_approval=False,  # Safe read operation
                reasoning="Detected case read intent. Routed to retrieve_case_details read tool.",
            )

        # 3. Check for COMBINED CASE COMPLIANCE CHECK
        if ("compliance" in q_lower or "policy check" in q_lower or "check policy" in q_lower) and re.search(r"(?:case|ticket)\s+#?(\d+)", q_lower):
            c_match = re.search(r"(?:case|ticket)\s+#?(\d+)", q_lower)
            case_id = int(c_match.group(1))
            return WorkflowRoutingDecision(
                intent=WorkflowIntent.COMPLIANCE_CASE_CHECK,
                requires_tool=True,
                tool_name="retrieve_case_details",
                tool_arguments={"case_id": case_id},
                requires_approval=False,
                reasoning="Detected compliance policy check for case. Routed to retrieve case and RAG.",
            )

        # 4. Default: RAG POLICY QUERY
        return WorkflowRoutingDecision(
            intent=WorkflowIntent.RAG_POLICY_QUERY,
            requires_tool=False,
            tool_name=None,
            tool_arguments={},
            requires_approval=False,
            reasoning="Detected informational policy inquiry. Routed to Policy RAG Assistant.",
        )
