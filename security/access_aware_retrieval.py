"""
Access-Aware Retrieval Module.
Enforces role-based and department-based policy access boundaries
before context reaches the LLM and prevents unauthorized citations.
"""
from typing import List, Dict, Any, Optional
from security.auth import UserPrincipal
from security.rbac import Role, Permission, check_permission


# Policy document sensitivity classifications
POLICY_PERMISSIONS: Dict[str, List[str]] = {
    "HR-POLICY-001": ["viewer", "agent", "manager", "admin"],
    "LEAVE-POLICY-002": ["viewer", "agent", "manager", "admin"],
    "EXPENSE-POLICY-003": ["viewer", "agent", "manager", "admin"],
    "TRAVEL-POLICY-004": ["viewer", "agent", "manager", "admin"],
    "IT-SECURITY-005": ["agent", "manager", "admin"],  # Sensitive technical infrastructure
    "COMPLIANCE-POLICY-006": ["manager", "admin"],     # Confidential whistleblower & AML investigations
}


class AccessAwarePolicyFilter:
    """
    Enforces authorization boundaries during document retrieval and citation formatting.
    """

    @staticmethod
    def get_allowed_document_ids(principal: UserPrincipal) -> List[str]:
        """Returns the list of document IDs the user is authorized to read."""
        user_role = principal.role.lower()
        allowed = []
        has_restricted = check_permission(principal, Permission.VIEW_RESTRICTED_POLICIES)

        for doc_id, roles in POLICY_PERMISSIONS.items():
            if user_role in roles or has_restricted:
                allowed.append(doc_id)
        return allowed

    @staticmethod
    def is_document_allowed(principal: UserPrincipal, document_id: str) -> bool:
        """Checks if a user is allowed to access a specific document ID."""
        allowed_docs = AccessAwarePolicyFilter.get_allowed_document_ids(principal)
        return document_id in allowed_docs

    @staticmethod
    def filter_retrieved_chunks(principal: UserPrincipal, chunks: List[Any]) -> List[Any]:
        """
        Post-retrieval scrubber:
        Removes any chunks from unauthorized documents before prompt assembly,
        preventing unauthorized information from entering context or citations.
        """
        allowed_docs = set(AccessAwarePolicyFilter.get_allowed_document_ids(principal))
        filtered = []
        for item in chunks:
            doc_id = getattr(item.chunk, "document_id", None)
            if doc_id in allowed_docs:
                filtered.append(item)
        return filtered
