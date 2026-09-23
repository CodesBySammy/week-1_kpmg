"""
Role-Based Access Control (RBAC) Module.
Defines formal enterprise roles, granular permissions, and authorization gates.
"""
from enum import Enum
from typing import Set, List, Union
from fastapi import HTTPException, status
from security.auth import UserPrincipal


class Role(str, Enum):
    VIEWER = "viewer"
    AGENT = "agent"
    MANAGER = "manager"
    ADMIN = "admin"


class Permission(str, Enum):
    READ_POLICY = "policy:read"
    READ_CASE = "case:read"
    INITIATE_WORKFLOW = "workflow:initiate"
    APPROVE_TICKET = "ticket:approve"
    EXECUTE_TICKET_UPDATE = "ticket:update"
    VIEW_RESTRICTED_POLICIES = "policy:restricted_read"
    ADMIN_OPERATIONS = "admin:all"


# Deterministic role-to-permission matrix
ROLE_PERMISSIONS: dict[str, Set[Permission]] = {
    Role.VIEWER.value: {
        Permission.READ_POLICY,
    },
    Role.AGENT.value: {
        Permission.READ_POLICY,
        Permission.READ_CASE,
        Permission.INITIATE_WORKFLOW,
    },
    Role.MANAGER.value: {
        Permission.READ_POLICY,
        Permission.READ_CASE,
        Permission.INITIATE_WORKFLOW,
        Permission.APPROVE_TICKET,
        Permission.EXECUTE_TICKET_UPDATE,
        Permission.VIEW_RESTRICTED_POLICIES,
    },
    Role.ADMIN.value: {
        Permission.READ_POLICY,
        Permission.READ_CASE,
        Permission.INITIATE_WORKFLOW,
        Permission.APPROVE_TICKET,
        Permission.EXECUTE_TICKET_UPDATE,
        Permission.VIEW_RESTRICTED_POLICIES,
        Permission.ADMIN_OPERATIONS,
    },
}


def get_user_permissions(principal: UserPrincipal) -> Set[Permission]:
    """Resolves all permissions for a user principal including extra permissions."""
    role_key = principal.role.lower()
    perms = set(ROLE_PERMISSIONS.get(role_key, set()))
    for p_str in principal.extra_permissions:
        try:
            perms.add(Permission(p_str))
        except ValueError:
            pass
    return perms


def check_permission(principal: UserPrincipal, required_permission: Union[Permission, str]) -> bool:
    """Checks if user has the required permission without raising an exception."""
    perm_val = Permission(required_permission) if isinstance(required_permission, str) else required_permission
    user_perms = get_user_permissions(principal)
    return perm_val in user_perms


def require_permission(principal: UserPrincipal, required_permission: Union[Permission, str]):
    """Enforces authorization gate, raising HTTP 403 Forbidden if not authorized."""
    if not check_permission(principal, required_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User '{principal.username}' with role '{principal.role}' lacks required permission '{required_permission}'.",
        )


def require_role(principal: UserPrincipal, allowed_roles: List[Union[Role, str]]):
    """Enforces that the user has at least one of the specified allowed roles."""
    role_strings = [r.value if isinstance(r, Role) else str(r).lower() for r in allowed_roles]
    if principal.role.lower() not in role_strings:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Action requires one of roles: {role_strings}. User has role '{principal.role}'.",
        )
