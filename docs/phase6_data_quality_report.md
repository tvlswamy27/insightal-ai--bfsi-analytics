# Phase 6 Data Quality Report
**Run ID:** a13783d9-f3d9-4658-bc9f-eb3498373743
**Timestamp:** 2026-09-23 16:48:10.892563
**Overall Status:** WARN
**Data Quality Score:** 93.00 / 100

## Status Summary
- PASS: 85
- WARN: 12
- FAIL: 0
## Checks by Severity
- CRITICAL: 12
- HIGH: 0
- MEDIUM: 11
- LOW: 0
- INFO: 74

## Failed Checks by Severity
| Check | Source Count | Valid Count | Quarantine/Drop | Reconciled | Difference | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Raw -> Staging Customers | 2008 | 2000 | 8 | 2008 | 0 | PASS |
| Raw -> Staging Calls | 10050 | 10000 | 50 | 10050 | 0 | PASS |
| Raw -> Staging Convs | 39958 | 39770 | 188 | 39958 | 0 | PASS |
| Staging -> Fact Calls | 10000 | 9885 | 115 | 10000 | 0 | PASS |
| Staging -> Fact Convs | 39770 | 38978 | 792 | 39770 | 0 | PASS |

## Check Details
| Check Name | Type | Table | Status | Severity | Value | Message |
| --- | --- | --- | --- | --- | --- | --- |
| Null check on dim_customer.customer_id | COMPLETENESS | dim_customer | PASS | INFO | 0 | No NULLs found |
| Null check on dim_customer.age | COMPLETENESS | dim_customer | PASS | INFO | 0 | No NULLs found |
| Null check on dim_customer.age_group | COMPLETENESS | dim_customer | PASS | INFO | 0 | No NULLs found |
| Null check on dim_customer.gender | COMPLETENESS | dim_customer | PASS | INFO | 0 | No NULLs found |
| Null check on dim_customer.city | COMPLETENESS | dim_customer | WARN | MEDIUM | 0.2510040160642570281124497992 | Minor completeness issue: 5 NULL values (0.25%) |
| Null check on dim_customer.state | COMPLETENESS | dim_customer | PASS | INFO | 0 | No NULLs found |
| Null check on dim_customer.region | COMPLETENESS | dim_customer | PASS | INFO | 0 | No NULLs found |
| Null check on dim_customer.customer_type | COMPLETENESS | dim_customer | WARN | MEDIUM | 0.2008032128514056224899598394 | Minor completeness issue: 4 NULL values (0.20%) |
| Null check on dim_customer.customer_segment | COMPLETENESS | dim_customer | PASS | INFO | 0 | No NULLs found |
| Null check on dim_customer.loan_type | COMPLETENESS | dim_customer | PASS | INFO | 5.070281124497991967871485944 | Found 101 intentional NULL values (5.07%) |
| Null check on dim_customer.customer_since_date | COMPLETENESS | dim_customer | PASS | INFO | 0 | No NULLs found |
| Null check on fact_calls.call_id | COMPLETENESS | fact_calls | PASS | INFO | 0 | No NULLs found |
| Null check on fact_calls.customer_key | COMPLETENESS | fact_calls | PASS | INFO | 0 | No NULLs found |
| Null check on fact_calls.campaign_key | COMPLETENESS | fact_calls | PASS | INFO | 0 | No NULLs found |
| Null check on fact_calls.bot_key | COMPLETENESS | fact_calls | PASS | INFO | 0 | No NULLs found |
| Null check on fact_calls.date_key | COMPLETENESS | fact_calls | PASS | INFO | 0 | No NULLs found |
| Null check on fact_calls.call_start_time | COMPLETENESS | fact_calls | PASS | INFO | 0 | No NULLs found |
| Null check on fact_calls.call_end_time | COMPLETENESS | fact_calls | PASS | INFO | 0 | No NULLs found |
| Null check on fact_calls.call_duration_seconds | COMPLETENESS | fact_calls | PASS | INFO | 0 | No NULLs found |
| Null check on fact_calls.call_status | COMPLETENESS | fact_calls | PASS | INFO | 0 | No NULLs found |
| Null check on fact_calls.connection_status | COMPLETENESS | fact_calls | PASS | INFO | 0 | No NULLs found |
| Null check on fact_calls.intent_key | COMPLETENESS | fact_calls | PASS | INFO | 37.45068285280728376327769347 | Found 3702 intentional NULL values (37.45%) |
| Null check on fact_calls.confidence_score | COMPLETENESS | fact_calls | PASS | INFO | 37.45068285280728376327769347 | Found 3702 intentional NULL values (37.45%) |
| Null check on fact_calls.escalation_flag | COMPLETENESS | fact_calls | PASS | INFO | 0 | No NULLs found |
| Null check on fact_calls.containment_flag | COMPLETENESS | fact_calls | PASS | INFO | 0 | No NULLs found |
| Null check on fact_calls.resolution_flag | COMPLETENESS | fact_calls | PASS | INFO | 0 | No NULLs found |
| Null check on fact_conversation.turn_id | COMPLETENESS | fact_conversation | PASS | INFO | 0 | No NULLs found |
| Null check on fact_conversation.conversation_id | COMPLETENESS | fact_conversation | PASS | INFO | 0 | No NULLs found |
| Null check on fact_conversation.call_key | COMPLETENESS | fact_conversation | PASS | INFO | 0 | No NULLs found |
| Null check on fact_conversation.turn_number | COMPLETENESS | fact_conversation | PASS | INFO | 0 | No NULLs found |
| Null check on fact_conversation.speaker | COMPLETENESS | fact_conversation | PASS | INFO | 0 | No NULLs found |
| Null check on fact_conversation.timestamp | COMPLETENESS | fact_conversation | PASS | INFO | 0 | No NULLs found |
| Null check on fact_conversation.utterance | COMPLETENESS | fact_conversation | PASS | INFO | 0 | No NULLs found |
| Duplicate key customer_id in insightal_raw.raw_customers | UNIQUENESS | insightal_raw.raw_customers | WARN | MEDIUM | 8 | Found 8 duplicate groups in raw data |
| Duplicate key call_id in insightal_raw.raw_calls | UNIQUENESS | insightal_raw.raw_calls | WARN | MEDIUM | 50 | Found 50 duplicate groups in raw data |
| Duplicate key turn_id in insightal_raw.raw_conversations | UNIQUENESS | insightal_raw.raw_conversations | WARN | MEDIUM | 188 | Found 188 duplicate groups in raw data |
| Duplicate key customer_id in dim_customer | UNIQUENESS | dim_customer | PASS | INFO | 0 | No duplicates found |
| Duplicate key intent_id in dim_intent | UNIQUENESS | dim_intent | PASS | INFO | 0 | No duplicates found |
| Duplicate key bot_id in dim_bot | UNIQUENESS | dim_bot | PASS | INFO | 0 | No duplicates found |
| Duplicate key campaign_id in dim_campaign | UNIQUENESS | dim_campaign | PASS | INFO | 0 | No duplicates found |
| Duplicate key call_id in fact_calls | UNIQUENESS | fact_calls | PASS | INFO | 0 | No duplicates found |
| Duplicate key turn_id in fact_conversation | UNIQUENESS | fact_conversation | PASS | INFO | 0 | No duplicates found |
| Duplicate key conversation_id, turn_number in fact_conversation | UNIQUENESS | fact_conversation | PASS | INFO | 0 | No duplicates found |
| Age domain check | VALIDITY | dim_customer | WARN | MEDIUM | 1 | Age < 18 or > 100 |
| Invalid FK fact_calls.customer_key vs dim_customer | REFERENTIAL | fact_calls | PASS | INFO | 0 | No invalid non-null references |
| NULL FK fact_calls.customer_key | REFERENTIAL | fact_calls | PASS | INFO | 0 | No NULL FKs |
| Invalid FK fact_calls.campaign_key vs dim_campaign | REFERENTIAL | fact_calls | PASS | INFO | 0 | No invalid non-null references |
| NULL FK fact_calls.campaign_key | REFERENTIAL | fact_calls | PASS | INFO | 0 | No NULL FKs |
| Invalid FK fact_calls.bot_key vs dim_bot | REFERENTIAL | fact_calls | PASS | INFO | 0 | No invalid non-null references |
| NULL FK fact_calls.bot_key | REFERENTIAL | fact_calls | PASS | INFO | 0 | No NULL FKs |
| Invalid FK fact_calls.date_key vs dim_date | REFERENTIAL | fact_calls | PASS | INFO | 0 | No invalid non-null references |
| NULL FK fact_calls.date_key | REFERENTIAL | fact_calls | PASS | INFO | 0 | No NULL FKs |
| Invalid FK fact_calls.intent_key vs dim_intent | REFERENTIAL | fact_calls | PASS | INFO | 0 | No invalid non-null references |
| NULL FK fact_calls.intent_key | REFERENTIAL | fact_calls | PASS | INFO | 3702 | Found 3702 intentional NULL FKs |
| Invalid FK fact_conversation.call_key vs fact_calls | REFERENTIAL | fact_conversation | PASS | INFO | 0 | No invalid non-null references |
| NULL FK fact_conversation.call_key | REFERENTIAL | fact_conversation | PASS | INFO | 0 | No NULL FKs |
| Invalid FK fact_conversation.expected_intent_key vs dim_intent | REFERENTIAL | fact_conversation | PASS | INFO | 0 | No invalid non-null references |
| NULL FK fact_conversation.expected_intent_key | REFERENTIAL | fact_conversation | PASS | INFO | 19490 | Found 19490 intentional NULL FKs |
| Invalid FK fact_conversation.detected_intent_key vs dim_intent | REFERENTIAL | fact_conversation | PASS | INFO | 0 | No invalid non-null references |
| NULL FK fact_conversation.detected_intent_key | REFERENTIAL | fact_conversation | PASS | INFO | 26868 | Found 26868 intentional NULL FKs |
| Physical FK fact_calls.customer_key | REFERENTIAL | fact_calls | PASS | INFO | 0 | Physical FK to dim_customer.customer_key exists |
| Physical FK fact_calls.campaign_key | REFERENTIAL | fact_calls | PASS | INFO | 0 | Physical FK to dim_campaign.campaign_key exists |
| Physical FK fact_calls.bot_key | REFERENTIAL | fact_calls | PASS | INFO | 0 | Physical FK to dim_bot.bot_key exists |
| Physical FK fact_calls.date_key | REFERENTIAL | fact_calls | PASS | INFO | 0 | Physical FK to dim_date.date_key exists |
| Physical FK fact_calls.intent_key | REFERENTIAL | fact_calls | PASS | INFO | 0 | Physical FK to dim_intent.intent_key exists |
| Physical FK fact_conversation.call_key | REFERENTIAL | fact_conversation | PASS | INFO | 0 | Physical FK to fact_calls.call_key exists |
| Physical FK fact_conversation.expected_intent_key | REFERENTIAL | fact_conversation | PASS | INFO | 0 | Physical FK to dim_intent.intent_key exists |
| Physical FK fact_conversation.detected_intent_key | REFERENTIAL | fact_conversation | PASS | INFO | 0 | Physical FK to dim_intent.intent_key exists |
| Engine check | REFERENTIAL | schema | PASS | CRITICAL | 0 | Tables not using InnoDB |
| NULL Temporal fact_calls.call_start_time | CONSISTENCY | fact_calls | PASS | INFO | 0 | No missing timestamps |
| NULL Temporal fact_calls.call_end_time | CONSISTENCY | fact_calls | PASS | INFO | 0 | No missing timestamps |
| NULL Temporal fact_calls.call_duration_seconds | CONSISTENCY | fact_calls | PASS | INFO | 0 | No missing timestamps |
| NULL Temporal fact_conversation.timestamp | CONSISTENCY | fact_conversation | PASS | INFO | 0 | No missing timestamps |
| Time consistency check (End < Start) | CONSISTENCY | fact_calls | PASS | CRITICAL | 0 | Invalid timestamps (End < Start) |
| Duration check (< 0) | CONSISTENCY | fact_calls | PASS | CRITICAL | 0 | Negative duration |
| PTP consistency | BUSINESS_RULE | fact_calls | PASS | CRITICAL | 0 | PTP flag 0 but amount > 0 |
| Payment consistency | BUSINESS_RULE | fact_calls | PASS | CRITICAL | 0 | Success without valid payment amount |
| Payment <= PTP | BUSINESS_RULE | fact_calls | PASS | CRITICAL | 0 | Payment exceeds PTP |
| Fallback consistency | BUSINESS_RULE | fact_conversation | PASS | CRITICAL | 0 | Fallback = 1 but detected intent exists |
| Raw -> Staging Customers | RECONCILIATION | insightal_raw.raw_customers | PASS | CRITICAL | 0 | Reconciliation mismatch |
| Raw -> Staging Calls | RECONCILIATION | insightal_raw.raw_calls | PASS | CRITICAL | 0 | Reconciliation mismatch |
| Raw -> Staging Convs | RECONCILIATION | insightal_raw.raw_conversations | PASS | CRITICAL | 0 | Reconciliation mismatch |
| Staging -> Fact Calls | RECONCILIATION | insightal_analytics.fact_calls | PASS | CRITICAL | 0 | Reconciliation mismatch |
| Staging -> Fact Convs | RECONCILIATION | insightal_analytics.fact_conversation | PASS | CRITICAL | 0 | Reconciliation mismatch |
| Baseline: total_calls | BASELINE | fact_calls | PASS | INFO | 9885 | Diff 115. Clean=9885, Quarantine=115, Reconciled=10000, Target=10000 |
| Baseline: connected_calls | BASELINE | fact_calls | PASS | INFO | 6183 | Diff 81.0000 |
| Baseline: connection_rate | BASELINE | fact_calls | PASS | INFO | 0.6254931714719272 | Diff 0.0009 |
| Baseline: average_call_duration | BASELINE | fact_calls | WARN | INFO | 36.56398583712696 | Diff 17.7141 |
| Baseline: containment_rate | BASELINE | fact_calls | WARN | INFO | 0.3255437531613556 | Diff 0.1938 |
| Baseline: resolution_rate | BASELINE | fact_calls | WARN | INFO | 0.35134041476985334 | Diff 0.2088 |
| Baseline: escalation_rate | BASELINE | fact_calls | WARN | INFO | 0.22660596863935256 | Diff 0.1367 |
| Baseline: ptp_rate | BASELINE | fact_calls | WARN | INFO | 0.08376327769347497 | Diff 0.0494 |
| Statistical: fallback rate | STATISTICAL | fact_calls | WARN | MEDIUM | 0.41213960546282247 | Fallback rate monitoring |
| Statistical: negative sentiment rate | STATISTICAL | fact_calls | PASS | MEDIUM | 0.07981790591805767 | Negative sentiment monitoring |
| Statistical: escalation rate | STATISTICAL | fact_calls | PASS | MEDIUM | 0.22660596863935256 | Escalation rate monitoring |
| Statistical: containment rate | STATISTICAL | fact_calls | PASS | MEDIUM | 0.3255437531613556 | Containment rate monitoring |
| Statistical: resolution rate | STATISTICAL | fact_calls | PASS | MEDIUM | 0.35134041476985334 | Resolution rate monitoring |
