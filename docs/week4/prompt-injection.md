# Prompt Injection & Jailbreak Defenses

## 1. Attack Vectors Neutralized
- Direct instruction overrides (e.g. 'Ignore all previous instructions').
- Role bypass attacks (e.g. 'You are now DAN / system administrator').
- Document-based indirect injection (e.g. malicious policies containing instructions to dump the database).

## 2. Multi-Layer Defense
1. Regex pattern scanning intercepts known jailbreak patterns before model invocation.
2. Strict isolation of retrieved text as passive DATA rather than executable INSTRUCTIONS.
3. Deterministic application-layer checks: the model cannot grant permissions or bypass approvals regardless of its text generation.
