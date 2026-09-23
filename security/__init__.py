"""
Security Subsystem for Week 4 Controlled AI Workflows.
Includes Authentication, Role-Based Access Control (RBAC), Access-Aware Retrieval,
and Prompt-Injection / Input Safety Guardrails.
"""

from .auth import UserPrincipal, authenticate_token, create_access_token
from .rbac import Role, Permission, check_permission, require_role
from .access_aware_retrieval import AccessAwarePolicyFilter
from .guardrails import InputGuardrail, SanitizedInput, GuardrailViolation

__all__ = [
    "UserPrincipal",
    "authenticate_token",
    "create_access_token",
    "Role",
    "Permission",
    "check_permission",
    "require_role",
    "AccessAwarePolicyFilter",
    "InputGuardrail",
    "SanitizedInput",
    "GuardrailViolation",
]
