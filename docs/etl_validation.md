# Phase 5 Validation Report

### A. Raw/staging/analytics row counts
| Metric / Check | Value / Violations | Status |
| --- | --- | --- |
| raw_customers | 2008 | INFO |
| raw_calls | 10050 | INFO |
| raw_conversations | 39958 | INFO |
| stg_customers | 2000 | INFO |
| stg_calls | 10000 | INFO |
| stg_conversations | 39770 | INFO |
| dim_customer | 1992 | INFO |
| dim_intent | 19 | INFO |
| dim_bot | 6 | INFO |
| dim_campaign | 7 | INFO |
| dim_date | 1095 | INFO |
| fact_calls | 9885 | INFO |
| fact_conversation | 38978 | INFO |

### B. Quarantine counts
| Metric / Check | Value / Violations | Status |
| --- | --- | --- |
| Quarantined stg_customers | 8 | INFO |
| Quarantined stg_calls | 115 | INFO |
| Quarantined stg_calls (Invalid Customer FK) | 0 | INFO |
| Quarantined stg_calls (Invalid Campaign FK) | 0 | INFO |
| Quarantined stg_calls (Invalid Bot FK) | 0 | INFO |
| Quarantined stg_calls (Invalid Date FK) | 0 | INFO |
| Quarantined stg_calls (Invalid Intent FK) | 0 | INFO |
| Quarantined stg_conversations | 792 | INFO |
| Quarantined stg_conversations (Invalid Call FK) | 0 | INFO |
| Quarantined stg_conversations (Invalid Expected Intent FK) | 0 | INFO |
| Quarantined stg_conversations (Invalid Detected Intent FK) | 0 | INFO |

### D. Physical FK constraints
| Metric / Check | Value / Violations | Status |
| --- | --- | --- |
| fact_calls -> dim_customer | 1 | PASS |
| fact_calls -> dim_campaign | 1 | PASS |
| fact_calls -> dim_bot | 1 | PASS |
| fact_calls -> dim_date | 1 | PASS |
| fact_calls -> dim_intent | 1 | PASS |
| fact_conversation -> fact_calls | 1 | PASS |
| fact_conversation -> dim_intent | 2 | PASS |

### E. Logical orphan checks
| Metric / Check | Value / Violations | Status |
| --- | --- | --- |
| CRITICAL: Orphan Calls vs Customer | 0 | PASS |
| CRITICAL: Orphan Calls vs Campaign | 0 | PASS |
| CRITICAL: Orphan Calls vs Bot | 0 | PASS |
| CRITICAL: Orphan Calls vs Date | 0 | PASS |
| CRITICAL: Orphan Calls vs Intent | 0 | PASS |
| CRITICAL: Orphan Conversations vs Call | 0 | PASS |
| CRITICAL: Orphan Conversations vs Expected Intent | 0 | PASS |
| CRITICAL: Orphan Conversations vs Detected Intent | 0 | PASS |

### F. Timestamp validation
| Metric / Check | Value / Violations | Status |
| --- | --- | --- |
| CRITICAL: Invalid Duration / End Time | 0 | PASS |

### G. Payment validation
| Metric / Check | Value / Violations | Status |
| --- | --- | --- |
| CRITICAL: Payment Success Rule Violations | 0 | PASS |
| CRITICAL: Payment Non-Success Violations | 0 | PASS |

### H. PTP validation
| Metric / Check | Value / Violations | Status |
| --- | --- | --- |
| CRITICAL: Invalid PTP Amount | 0 | PASS |
| CRITICAL: PTP Amount Missing | 0 | PASS |
| CRITICAL: Payment exceeds PTP | 0 | PASS |

### I. Intent/fallback validation
| Metric / Check | Value / Violations | Status |
| --- | --- | --- |
| CRITICAL: Intent Fallback Violations | 0 | PASS |

### J. Database engine validation
No issues found or no data.

### C. Row-count reconciliation
*(Reconciliation check between Raw -> Staging -> Quarantine -> Analytics)*

10,000 staging calls - 115 quarantined calls = 9885 fact_calls
**Status:** PASS

39,770 staging conversations - 792 quarantined conversations = 38978 fact_conversation
**Status:** PASS

### K. ETL execution status
**PHASE 5 ETL STATUS: PASS**
