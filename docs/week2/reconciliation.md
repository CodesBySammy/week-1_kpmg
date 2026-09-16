# Source-to-Target Reconciliation Engine: Mathematical Integrity Verification

## 1. Overview & Verification Formulae

The `ReconciliationEngine` (`pipeline/reconciliation/reconciler.py`) mathematically balances record counts across all processing stages to verify zero data loss.

$$\begin{aligned}
\textbf{Equation 1: } & \text{Source Count} = \text{Valid Count} + \text{Quarantined Count} \\
\textbf{Equation 2: } & \text{Curated Count} = \text{Valid Count} - \text{Duplicates Removed}
\end{aligned}$$

---

## 2. Production Execution Evidence

In our verified test execution of `cases.csv`:
- **Source Count Ingested**: 20
- **Quarantined Count**: 5
- **Valid Passed Count**: 15 ($20 = 15 + 5$, **Source Variance = 0 $\rightarrow$ BALANCED**)
- **Duplicates Removed**: 1 (case_id 1 latest timestamp preserved)
- **Curated Published Count**: 14 ($14 = 15 - 1$, **Curated Variance = 0 $\rightarrow$ BALANCED**)
- **Overall Reconciliation Status**: `🟢 PASS`

---

## 3. Automated Reporting

The engine publishes both:
1. `reports/reconciliation/reconciliation_<run_id>.json`: For automated monitoring agents and alerting bots.
2. `reports/reconciliation/reconciliation_<run_id>.md`: For human inspection, Git pull requests, and audit logs.
