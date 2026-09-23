"""
Unit and Integration Tests for Week 4 Security, RBAC, and Access-Aware Retrieval.

Verifies:
  1. HMAC-SHA256 token issuance and validation.
  2. Role permissions (viewer, agent, manager, admin).
  3. Strict authorization enforcement (check_permission, require_role).
  4. Access-aware retrieval (pre-filtering and post-retrieval scrubbing).
"""

import pytest
from fastapi import HTTPException

from security.access_aware_retrieval import AccessAwarePolicyFilter
from security.auth import UserPrincipal, authenticate_token, create_access_token
from security.rbac import Permission, Role, check_permission, require_role


def test_jwt_hmac_token_issuance_and_decode():
    """Verify bearer token creation and signature verification."""
    token = create_access_token(user_id=42, username="sam", email="sam@example.com", role="agent")
    principal = authenticate_token(token)

    assert principal.user_id == 42
    assert principal.username == "sam"
    assert principal.role == "agent"


def test_jwt_tampered_token_fails():
    """Verify tampered bearer tokens are rejected."""
    token = create_access_token(user_id=42, username="sam", email="sam@example.com", role="agent")
    tampered = token[:-4] + "wxyz"

    with pytest.raises(HTTPException) as exc_info:
        authenticate_token(tampered)
    assert exc_info.value.status_code == 401


def test_role_permissions_matrix():
    """Verify granular permissions for all 4 enterprise roles."""
    viewer = UserPrincipal(user_id=1, username="v", email="v@ex.com", role="viewer")
    agent = UserPrincipal(user_id=2, username="a", email="a@ex.com", role="agent")
    manager = UserPrincipal(user_id=3, username="m", email="m@ex.com", role="manager")
    admin = UserPrincipal(user_id=4, username="adm", email="adm@ex.com", role="admin")

    # 1. Viewer: read policy only, no case updates, no approvals
    assert check_permission(viewer, Permission.READ_POLICY) is True
    assert check_permission(viewer, Permission.EXECUTE_TICKET_UPDATE) is False
    assert check_permission(viewer, Permission.APPROVE_TICKET) is False

    # 2. Agent: read policy, read case, initiate workflow, cannot approve
    assert check_permission(agent, Permission.READ_POLICY) is True
    assert check_permission(agent, Permission.READ_CASE) is True
    assert check_permission(agent, Permission.APPROVE_TICKET) is False

    # 3. Manager: approve ticket, execute update, restricted policy read
    assert check_permission(manager, Permission.APPROVE_TICKET) is True
    assert check_permission(manager, Permission.EXECUTE_TICKET_UPDATE) is True
    assert check_permission(manager, Permission.VIEW_RESTRICTED_POLICIES) is True

    # 4. Admin: full operations
    assert check_permission(admin, Permission.ADMIN_OPERATIONS) is True


def test_require_role_enforcement():
    """Verify require_role raises 403 for unauthorized roles."""
    agent = UserPrincipal(user_id=2, username="a", email="a@ex.com", role="agent")
    manager = UserPrincipal(user_id=3, username="m", email="m@ex.com", role="manager")

    # Agent attempting an action restricted to manager
    with pytest.raises(HTTPException) as exc:
        require_role(agent, [Role.MANAGER, Role.ADMIN])
    assert exc.value.status_code == 403
    assert "Forbidden" in exc.value.detail or "requires one of roles" in exc.value.detail

    # Manager allowed
    require_role(manager, [Role.MANAGER, Role.ADMIN])


def test_access_aware_retrieval_filtering():
    """Verify role-based filtering on policy documents."""
    viewer = UserPrincipal(user_id=1, username="v", email="v@ex.com", role="viewer")
    agent = UserPrincipal(user_id=2, username="a", email="a@ex.com", role="agent")
    manager = UserPrincipal(user_id=3, username="m", email="m@ex.com", role="manager")

    viewer_docs = AccessAwarePolicyFilter.get_allowed_document_ids(viewer)
    agent_docs = AccessAwarePolicyFilter.get_allowed_document_ids(agent)
    manager_docs = AccessAwarePolicyFilter.get_allowed_document_ids(manager)

    # Viewer can see HR and leave policies, but NOT IT security or compliance
    assert "HR-POLICY-001" in viewer_docs
    assert "IT-SECURITY-005" not in viewer_docs
    assert "COMPLIANCE-POLICY-006" not in viewer_docs

    # Agent can see IT security, but NOT sensitive compliance whistleblower investigations
    assert "IT-SECURITY-005" in agent_docs
    assert "COMPLIANCE-POLICY-006" not in agent_docs

    # Manager can see all including COMPLIANCE-POLICY-006
    assert "COMPLIANCE-POLICY-006" in manager_docs
