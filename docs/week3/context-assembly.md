# Token-Bounded Context Assembly

## 1. Budget Management
LLM context windows are bounded resources. The `ContextAssembler`:
- Enforces hard token limits (`max_context_tokens`, default 2,000).
- Formats evidence passages with explicit source tags:
  ```xml
  <source id="TRAVEL-POLICY-004" section="Section 2.1">
  All business flights exceeding 6 hours are eligible for Business Class...
  </source>
  ```
- Truncates lower-ranked passages gracefully when the budget is reached.
