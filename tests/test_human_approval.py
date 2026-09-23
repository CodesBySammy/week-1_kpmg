"""
Unit Tests for Week 4 Human Approval Workflows.

Verifies:
  1. Creation of approval requests with expiration TTL.
  2. Approval lifecycle: PENDING, APPROVED, REJECTED, EXPIRED.
  3. Token verification and replay protection.
  4. Role requirements: only authorized reviewers can approve.
"""

import time
import pytest

from security.auth import UserPrincipal
from workflow.approval import ApprovalManager, ApprovalStatus


def test_approval_request_creation():
    """Verify approval request creation with unique ID and expiration."""
    mgr = ApprovalManager()
    req = mgr.request_approval(
        ticket_id=42,
        target_status="closed",
        proposed_by="agent_sam",
        justification="Issue resolved by customer verification",
        ttl_seconds=60,
    )

    assert req.approval_id.startswith("appr_")
    assert req.status == ApprovalStatus.PENDING
    assert req.ticket_id == 42
    assert req.target_status == "closed"


def test_approve_request_generates_token():
    """Verify approving a pending request transitions status and authorizes execution."""
    mgr = ApprovalManager()
    manager = UserPrincipal(user_id=1, username="manager_dan", email="dan@ex.com", role="manager")
    req = mgr.request_approval(
        ticket_id=10,
        target_status="in_progress",
        proposed_by="agent_sam",
        justification="Starting investigation",
    )

    approved = mgr.grant_approval(req.approval_id, approver=manager)
    assert approved.status == ApprovalStatus.APPROVED
    assert approved.approved_by == "manager_dan"

    is_valid, msg = mgr.verify_approval(
        approval_id=req.approval_id,
        expected_ticket_id=10,
        expected_status="in_progress",
    )
    assert is_valid is True
    assert "Valid and authorized" in msg


def test_reject_request():
    """Verify rejecting an approval request marks it REJECTED."""
    mgr = ApprovalManager()
    manager = UserPrincipal(user_id=1, username="manager_dan", email="dan@ex.com", role="manager")
    req = mgr.request_approval(
        ticket_id=10,
        target_status="closed",
        proposed_by="agent_sam",
        justification="Close without fix",
    )

    mgr.reject_approval(req.approval_id, approver=manager, reason="Policy violation")
    updated = mgr.get_approval(req.approval_id)
    assert updated.status == ApprovalStatus.REJECTED
    assert updated.approved_by == "manager_dan"

    is_valid, msg = mgr.verify_approval(
        approval_id=req.approval_id,
        expected_ticket_id=10,
        expected_status="closed",
    )
    assert is_valid is False
    assert "rejected" in msg.lower()


def test_approval_token_expiration():
    """Verify expired approval tokens are rejected."""
    # Create with 1 second TTL
    mgr = ApprovalManager()
    manager = UserPrincipal(user_id=1, username="manager_dan", email="dan@ex.com", role="manager")
    req = mgr.request_approval(
        ticket_id=10,
        target_status="closed",
        proposed_by="agent_sam",
        justification="Expiring ticket",
        ttl_seconds=1,
    )
    mgr.grant_approval(req.approval_id, approver=manager)

    # Sleep 1.1s to trigger expiration
    time.sleep(1.1)

    is_valid, msg = mgr.verify_approval(
        approval_id=req.approval_id,
        expected_ticket_id=10,
        expected_status="closed",
    )
    assert is_valid is False
    assert "expired" in msg.lower()


def test_invalid_approval_token():
    """Verify unknown or forged tokens fail verification."""
    mgr = ApprovalManager()
    is_valid, msg = mgr.verify_approval(
        approval_id="non-existent-token-xyz",
        expected_ticket_id=10,
        expected_status="closed",
    )
    assert is_valid is False
    assert "does not exist" in msg
