# Complete Data Dictionary
**Project:** Insightal AI — Conversational AI & BFSI Voice Analytics Platform

## 1. Scope & Table Grains
This data dictionary is the authoritative specification for the synthetic data generator, MySQL schema, SQL transformations, Python analytics, ML pipeline, and Power BI model.

### Table Grains
- **`fact_calls`**: One row = one complete voice call interaction.
- **`fact_conversation`**: One row = one conversational turn/utterance.
- **`dim_customer`**: One row = one synthetic customer.
- **`dim_intent`**: One row = one business/AI intent.
- **`dim_bot`**: One row = one bot/version/language/model configuration.
- **`dim_campaign`**: One row = one campaign.
- **`dim_date`**: One row = one calendar date.

---

## 2. Raw & Staging Layer Rules

### 2.1 Raw Layer
Raw tables preserve generated data as-is. They may contain intentional data-quality issues (duplicates, missing values, invalid timestamps, invalid IDs) and are not trusted for BI. 

> **Lineage Note:** Raw and staging columns inherit their business definitions, domains, and validation rules from their corresponding source/target analytics fields unless explicitly overridden by staging transformation rules.

- **`raw_customers`** (9 columns): `customer_id`, `age`, `gender`, `city`, `state`, `customer_type`, `customer_segment`, `loan_type`, `customer_since_date`.
- **`raw_calls`** (24 columns): `call_id`, `customer_id`, `campaign_id`, `bot_id`, `call_date`, `call_time`, `call_duration_seconds`, `call_status`, `connection_status`, `hangup_reason`, `attempt_number`, `outstanding_amount_at_call`, `days_past_due_at_call`, `ptp_flag`, `ptp_amount`, `payment_status`, `payment_amount`, `identity_verified_flag`, `task_started_flag`, `task_completed_flag`, `resolution_flag`, `fallback_flag`, `escalation_flag`, `sentiment_score`.
- **`raw_conversations`** (14 columns): `turn_id`, `conversation_id`, `call_id`, `turn_number`, `speaker`, `timestamp`, `utterance`, `expected_intent_id`, `detected_intent_id`, `confidence_score`, `sentiment`, `sentiment_score`, `fallback_flag`, `escalation_trigger_flag`.

### 2.2 Staging Layer
Transforms data from raw for analytics ingestion. Performs type casting, null handling, deduplication of exact rows, and timestamp normalization. Invalid value detection flags values outside domain ranges. Bad records are flagged and quarantined.

- **`stg_customers`** (10 columns): All 9 from `raw_customers` + `error_flag`.
- **`stg_calls`** (25 columns): All 24 from `raw_calls` + `error_flag`.
- **`stg_conversations`** (15 columns): All 14 from `raw_conversations` + `error_flag`.

---

## 3. Analytics Layer: Fully Documented Tables

### 3.1 `fact_calls`
| Column | Type | Null | Key | Definition | Source/Gen Rule | Allowed/Example | Validation | KPI Usage | ML Elig | Leakage | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `call_key` | BIGINT | N | PK | Surrogate key | Derived Auto-inc | Ex: 10001 | Unique > 0 | None | Prohibited | ID | - |
| `call_id` | VARCHAR | N | UK | Natural identifier | Synthetic UUID | Ex: 'c-1234-xyz' | Unique | Total Calls | Prohibited | ID | - |
| `customer_key` | INT | N | FK | Link to dim_customer | Derived join | Ex: 101 | Exists in dim | None | Allowed | None | - |
| `campaign_key` | INT | N | FK | Link to dim_campaign | Derived join | Ex: 5 | Exists in dim | Campaign filtering | Allowed | None | - |
| `bot_key` | INT | N | FK | Link to dim_bot | Derived join | Ex: 2 | Exists in dim | Bot grouping | Allowed | None | - |
| `date_key` | INT | N | FK | Link to dim_date | Derived (YYYYMMDD) | Ex: 20260115 | Exists in dim | Trending | Allowed | None | - |
| `intent_key` | INT | Y | FK | Primary call intent | Derived join | Ex: 10 | Exists in dim | Intent grouping | Allowed | None | - |
| `call_start_time` | DATETIME | N | - | Call start timestamp | Synthetic | Ex: '2026-01-15 10:00:00'| <= call_end_time | None | Allowed | None | - |
| `call_end_time` | DATETIME | N | - | Call end timestamp | Synthetic | Ex: '2026-01-15 10:05:00'| >= call_start_time | None | Prohibited | Post-outcome | - |
| `call_duration_seconds`| INT | N | - | Total call duration | end - start | Ex: 300 | >= 0 | Avg Duration | Prohibited | Post-outcome | - |
| `call_status` | VARCHAR | N | - | Final disposition | Synthetic | 'Completed', 'Failed' | In domain | None | Prohibited | Post-outcome | - |
| `connection_status` | VARCHAR | N | - | Reachability | Synthetic | 'Connected', 'Voicemail' | In domain | Connection Rate | Prohibited | Post-outcome | - |
| `hangup_reason` | VARCHAR | Y | - | Why call ended | Synthetic | 'Customer Hung Up' | In domain | None | Prohibited | Post-outcome | - |
| `attempt_number` | INT | N | - | Attempt sequence | Synthetic | 1-10 | >= 1 | Avg Attempts | Allowed | None | - |
| `confidence_score` | DECIMAL | Y | - | Final avg confidence | Synthetic | 0.0 - 1.0 | 0 to 1 | Avg Confidence | Prohibited | Post-outcome | Aggregated from turns |
| `outstanding_amount_at_call`| DECIMAL| Y | - | Debt snapshot | Synthetic snapshot | Ex: 5000.00 | >= 0 | Outstanding Amt | Allowed | None | Snapshotted at call |
| `days_past_due_at_call`| INT | Y | - | DPD snapshot | Synthetic snapshot | Ex: 45 | >= 0 | None | Allowed | None | Snapshotted at call |
| `dpd_bucket_at_call`| VARCHAR | Y | - | Bucket snapshot | Derived | '31-60', '0-30' | In domain | Collections filter | Allowed | None | - |
| `risk_segment_at_call`| VARCHAR | Y | - | Risk snapshot | Derived | 'High', 'Low' | In domain | Collections filter | Allowed | None | - |
| `identity_verified_flag`| BOOLEAN| N | - | Customer verified | Synthetic | 0, 1 | 0 or 1 | None | Prohibited | Post-outcome | - |
| `task_started_flag` | BOOLEAN| N | - | Task initiated | Synthetic | 0, 1 | 0 or 1 | Task Completion | Prohibited | Post-outcome | - |
| `task_completed_flag`| BOOLEAN| N | - | Task successful | Synthetic | 0, 1 | 0 or 1 (0 if start=0)| Task Completion | Prohibited | Post-outcome | - |
| `resolution_flag` | BOOLEAN| N | - | Call resolved | Synthetic | 0, 1 | 0 or 1 | Resolution Rate | Prohibited | Post-outcome | - |
| `fallback_flag` | BOOLEAN| N | - | Any fallback occurred| Derived | 0, 1 | 0 or 1 | None | Prohibited | Post-outcome | Rollup from turns |
| `escalation_flag` | BOOLEAN| N | - | Human transferred | Synthetic | 0, 1 | 0 or 1 | Escalation Rate | **TARGET** | Target | ML target variable |
| `containment_flag` | BOOLEAN| N | - | AI Contained | Derived | 0, 1 | 0 or 1 (0 if esc=1)| Containment Rate | Prohibited | Post-outcome | - |
| `sentiment` | VARCHAR | Y | - | Overall sentiment | Synthetic | 'Positive', 'Negative' | In domain | Satisfaction | Prohibited | Post-outcome | - |
| `sentiment_score` | DECIMAL| Y | - | Numerical sentiment | Synthetic | -1.0 to 1.0 | -1 to 1 | None | Prohibited | Post-outcome | - |
| `ptp_flag` | BOOLEAN| N | - | PTP secured | Synthetic | 0, 1 | 0 or 1 | PTP Rate | Prohibited | Post-outcome | - |
| `ptp_amount` | DECIMAL| Y | - | Promised amt | Synthetic | Ex: 1000.00 | >= 0 (Null if flag=0)| PTP Amount | Prohibited | Post-outcome | - |
| `payment_status` | VARCHAR| Y | - | Downstream payment | Synthetic | 'Success', 'Failed' | In domain | Successful PTP | Prohibited | Post-outcome | - |
| `payment_amount` | DECIMAL| Y | - | Actual paid amt | Synthetic | Ex: 1000.00 | >= 0 (Null if !=Succ)| Collection Amt | Prohibited | Post-outcome | - |

### 3.2 `fact_conversation`
**Confidence & Intent Semantics:** Turn-level confidence, intents, and sentiments belong strictly to **Customer** utterances (where the AI classifies the customer's input). Bot turns will have NULL for `expected_intent_key`, `detected_intent_key`, and `confidence_score` (unless explicitly modeling separate Bot self-confidence, which is excluded from MVP).

| Column | Type | Null | Key | Definition | Source/Gen Rule | Allowed/Example | Validation | KPI Usage | ML Elig | Leakage | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `turn_key` | BIGINT | N | PK | Surrogate key | Derived Auto-inc | Ex: 50001 | Unique | None | Prohibited | ID | - |
| `turn_id` | VARCHAR | N | UK | Natural turn ID | Synthetic UUID | Ex: 't-999-abc' | Unique | None | Prohibited | ID | - |
| `conversation_id` | VARCHAR | N | - | Call/Convo ID | Synthetic UUID | Ex: 'c-1234-xyz' | Matches call_id | None | Prohibited | ID | Identifies the overall call |
| `call_key` | BIGINT | N | FK | Link to fact_calls | Derived join | Ex: 10001 | Exists in calls | None | Prohibited | ID | - |
| `turn_number` | INT | N | - | Sequence in call | Synthetic | 1, 2, 3... | >= 1 | None | Allowed | None | - |
| `speaker` | VARCHAR | N | - | Utterance source | Synthetic | 'Customer', 'Bot'| In domain | Intent Acc (filter) | Allowed | None | - |
| `timestamp` | DATETIME | N | - | Utterance time | Synthetic | Ex: '2026-01-15...' | None | None | Allowed | None | - |
| `utterance` | TEXT | Y | - | Transcript text | Synthetic | "I want to pay" | None | None | Prohibited | Text | Excluded from ML structure |
| `expected_intent_key`| INT | Y | FK | Ground-truth intent | Synthetic | Ex: 10 | Exists in dim | Intent Accuracy | **Prohibited**| Ground Truth | Causes target leakage if used |
| `detected_intent_key`| INT | Y | FK | AI prediction | Synthetic | Ex: 10 | Exists in dim | Intent Accuracy | Allowed | None | Follows Option B |
| `confidence_score` | DECIMAL| Y | - | AI Turn Confidence | Synthetic | 0.0 - 1.0 | 0 to 1 | Avg Confidence | Allowed | None | Generated for Customer turns |
| `sentiment` | VARCHAR | Y | - | Turn sentiment | Synthetic | 'Positive' | In domain | None | Allowed | None | - |
| `sentiment_score` | DECIMAL| Y | - | Turn sentiment num | Synthetic | -1.0 to 1.0 | -1 to 1 | None | Allowed | None | - |
| `fallback_flag` | BOOLEAN| N | - | Triggered fallback | Synthetic | 0, 1 | 0 or 1 | Fallback Rate | Allowed | None | - |
| `escalation_trigger_flag`| BOOLEAN| N| - | Turn caused trigger| Synthetic | 0, 1 | 0 or 1 | None | Prohibited | Post-outcome | - |

### 3.3 `dim_customer`
| Column | Type | Null | Key | Definition | Source/Gen Rule | Allowed/Example | Validation | KPI Usage | ML Elig | Leakage |
|---|---|---|---|---|---|---|---|---|---|---|
| `customer_key` | INT | N | PK | Surrogate key | Derived Auto-inc | Ex: 101 | Unique | None | Prohibited | ID |
| `customer_id` | VARCHAR | N | UK | Natural ID | Synthetic UUID | Ex: 'cust-555' | Unique | None | Prohibited | ID |
| `age` | INT | N | - | Customer age | Synthetic | 18 - 80 | >= 18 | None | Allowed | None |
| `age_group` | VARCHAR | N | - | Binned age | Derived | '18-25', '26-35' | In domain | None | Allowed | None |
| `gender` | VARCHAR | N | - | Gender | Synthetic | 'M', 'F', 'O' | In domain | None | Allowed | None |
| `city` | VARCHAR | N | - | Synthetic City | Synthetic | 'Mumbai' | In domain | None | Allowed | None |
| `state` | VARCHAR | N | - | Synthetic State | Synthetic | 'Maharashtra' | In domain | None | Allowed | None |
| `region` | VARCHAR | N | - | Geographic region | Derived | 'West', 'South' | In domain | None | Allowed | None |
| `customer_type` | VARCHAR | N | - | Type of client | Synthetic | 'Retail' | In domain | None | Allowed | None |
| `customer_segment` | VARCHAR | N | - | Value grouping | Synthetic | 'High Value' | In domain | None | Allowed | None |
| `loan_type` | VARCHAR | N | - | Product category | Synthetic | 'Personal Loan' | In domain | None | Allowed | None |
| `customer_since_date`| DATE | N | - | Onboarding date | Synthetic | Ex: '2020-01-01' | <= today | None | Allowed | None |

### 3.4 `dim_intent`
| Column | Type | Null | Key | Definition | Source/Gen Rule | Allowed/Example | Validation | KPI Usage | ML Elig | Leakage |
|---|---|---|---|---|---|---|---|---|---|---|
| `intent_key` | INT | N | PK | Surrogate key | Derived Auto-inc | Ex: 10 | Unique | None | Prohibited | ID |
| `intent_id` | VARCHAR | N | UK | Natural ID | Synthetic | 'INT_PAYMENT' | Unique | None | Prohibited | ID |
| `intent_name` | VARCHAR | N | - | Display name | Synthetic | 'Promise to Pay' | None | Intent Accuracy | Allowed | None |
| `intent_category` | VARCHAR | N | - | Logical grouping | Synthetic | 'Collections' | In domain | None | Allowed | None |
| `business_function`| VARCHAR | N | - | Department | Synthetic | 'Debt Recovery' | In domain | None | Allowed | None |
| `expected_task` | VARCHAR | N | - | AI goal | Synthetic | 'Capture Date' | None | None | Allowed | None |

### 3.5 `dim_bot`
| Column | Type | Null | Key | Definition | Source/Gen Rule | Allowed/Example | Validation | KPI Usage | ML Elig | Leakage |
|---|---|---|---|---|---|---|---|---|---|---|
| `bot_key` | INT | N | PK | Surrogate key | Derived Auto-inc | Ex: 2 | Unique | None | Prohibited | ID |
| `bot_id` | VARCHAR | N | UK | Natural ID | Synthetic | 'BOT_V1' | Unique | None | Prohibited | ID |
| `bot_name` | VARCHAR | N | - | Bot display name | Synthetic | 'Insightal Voice' | None | None | Allowed | None |
| `bot_version` | VARCHAR | N | - | Version tag | Synthetic | 'v1.1' | None | Filtering | Allowed | None |
| `language` | VARCHAR | N | - | Spoken language | Synthetic | 'English', 'Hindi'| In domain | None | Allowed | None |
| `model_type` | VARCHAR | N | - | AI Architecture | Synthetic | 'Generative' | In domain | None | Allowed | None |
| `deployment_date` | DATE | N | - | Go-live date | Synthetic | '2025-06-01' | <= today | None | Allowed | None |

### 3.6 `dim_campaign`
| Column | Type | Null | Key | Definition | Source/Gen Rule | Allowed/Example | Validation | KPI Usage | ML Elig | Leakage |
|---|---|---|---|---|---|---|---|---|---|---|
| `campaign_key` | INT | N | PK | Surrogate key | Derived Auto-inc | Ex: 5 | Unique | None | Prohibited | ID |
| `campaign_id` | VARCHAR | N | UK | Natural ID | Synthetic | 'CAMP_001' | Unique | None | Prohibited | ID |
| `campaign_name` | VARCHAR | N | - | Display name | Synthetic | 'Q3 Collections' | None | Filtering | Allowed | None |
| `campaign_type` | VARCHAR | N | - | Campaign style | Synthetic | 'Loan Collections'| In domain | PTP Denom | Allowed | None |
| `business_unit` | VARCHAR | N | - | Sponsoring org | Synthetic | 'Retail Banking' | In domain | None | Allowed | None |
| `start_date` | DATE | N | - | Campaign start | Synthetic | '2026-01-01' | <= end_date| None | Allowed | None |
| `end_date` | DATE | Y | - | Campaign end | Synthetic | '2026-03-31' | >= start_date| None | Allowed | None |
| `target_segment` | VARCHAR | N | - | Audience spec | Synthetic | 'DPD 60-90' | In domain | None | Allowed | None |

### 3.7 `dim_date`
| Column | Type | Null | Key | Definition | Source/Gen Rule | Allowed/Example | Validation | KPI Usage | ML Elig | Leakage |
|---|---|---|---|---|---|---|---|---|---|---|
| `date_key` | INT | N | PK | Surrogate key | YYYYMMDD | 20260115 | Unique | None | Prohibited | ID |
| `date` | DATE | N | - | Actual date | Calendar Gen | '2026-01-15' | None | None | Allowed | None |
| `day` | INT | N | - | Day of month | Extracted | 1 - 31 | 1 to 31 | None | Allowed | None |
| `day_name` | VARCHAR | N | - | Day of week | Extracted | 'Monday' | In domain | None | Allowed | None |
| `week` | INT | N | - | Week of year | Extracted | 1 - 52 | 1 to 52 | None | Allowed | None |
| `month` | INT | N | - | Month num | Extracted | 1 - 12 | 1 to 12 | None | Allowed | None |
| `month_name` | VARCHAR | N | - | Month label | Extracted | 'January' | In domain | None | Allowed | None |
| `month_number` | INT | N | - | Month num (dup) | Extracted | 1 - 12 | 1 to 12 | None | Allowed | None |
| `quarter` | INT | N | - | Calendar Qtr | Extracted | 1 - 4 | 1 to 4 | None | Allowed | None |
| `year` | INT | N | - | Calendar Year | Extracted | 2026 | > 2000 | None | Allowed | None |
| `financial_year` | VARCHAR | N | - | IND FY (Apr-Mar) | Derived | 'FY25-26' | None | None | Allowed | None |
| `is_weekend` | BOOLEAN| N | - | Weekend flag | Derived | 0, 1 | 0 or 1 | None | Allowed | None |

---

## 4. Fallback Intent Handling
**Decision (Option B):** 
When a fallback occurs, `detected_intent_key` remains `NULL` and `fallback_flag` is set to `1`. 
*Reasoning:* This cleanly distinguishes intents the AI actively predicted from system failures, preventing "Fallback" from masquerading as a true intent classification in machine learning evaluations.

---

## 5. Eligible-Call Rules
Definitions for denominators used across KPIs:

- **Containment / Escalation / Resolution Eligibility:**
  - *Condition:* `connection_status = 'Connected' AND call_duration_seconds >= 5`
  - *Edge Cases:* Calls that connect but drop immediately (e.g., under 5 seconds) are not eligible for containment/escalation calculations as no true interaction occurred.
- **Task Completion Eligibility:**
  - *Condition:* `task_started_flag = 1`
  - *Edge Cases:* If a customer hangs up before the bot can even identify and start the task, it does not penalize task completion rate.
- **Fallback / Confidence Eligibility:**
  - *Condition:* `speaker = 'Customer'`
  - *Edge Cases:* Bot utterances do not trigger fallbacks and are not evaluated for intent confidence.
- **Collections Eligibility:**
  - *Condition:* `connection_status = 'Connected' AND dim_campaign.campaign_type = 'Loan Collections'`
  - *Edge Cases:* PTP metrics only apply to collections campaigns.

---

## 6. KPI → Data Dictionary Mapping (23 Metrics)
### Operational (6)
| KPI | Formula / Concept | Numerator | Denominator | Source Table | Source Columns | Grain | Eligibility / Edge Cases |
|---|---|---|---|---|---|---|---|
| **Total Calls** | Count | `COUNT(call_key)` | N/A | `fact_calls` | `call_key` | Call | None |
| **Connected Calls** | Count | `COUNT(call_key WHERE Connected)` | N/A | `fact_calls` | `connection_status` | Call | `status='Connected'` |
| **Connection Rate** | Num / Denom | `Connected Calls` | `Total Calls` | `fact_calls` | `connection_status` | Call | None |
| **Avg Call Duration**| Avg | `SUM(call_duration_seconds)` | `Connected Calls` | `fact_calls` | `call_duration_seconds` | Call | `status='Connected'` |
| **Median Duration** | Median | `MEDIAN(call_duration_seconds)`| N/A | `fact_calls` | `call_duration_seconds` | Call | `status='Connected'` |
| **Average Attempts** | Avg of Max | `SUM(MAX(attempt_number))` | `COUNT(DISTINCT customer_key)` | `fact_calls` | `attempt_number` | Cust | Groups calls by customer, takes the MAX attempt per customer, and averages that. |

### AI (7)
| KPI | Formula / Concept | Numerator | Denominator | Source Table | Source Columns | Grain | Eligibility / Edge Cases |
|---|---|---|---|---|---|---|---|
| **Intent Recog Acc** | Num / Denom | `SUM(expected = detected)` | `COUNT(eligible_turns)` | `fact_conversation` | `expected_intent_key`, `detected_intent_key`, `speaker`| Turn | `speaker='Customer' AND expected IS NOT NULL AND detected IS NOT NULL` |
| **Avg Confidence** | Avg | `SUM(confidence_score)` | `COUNT(confidence_score)` | `fact_conversation` | `confidence_score` | Turn | `speaker='Customer' AND confidence_score IS NOT NULL` |
| **Fallback Rate** | Num / Denom | `SUM(fallback_flag)` | `COUNT(eligible_turns)` | `fact_conversation` | `fallback_flag`, `speaker` | Turn | `speaker='Customer'` |
| **Containment Rate** | Num / Denom | `SUM(containment_flag)` | `Eligible Connected Calls` | `fact_calls` | `containment_flag` | Call | `duration >= 5` |
| **Escalation Rate** | Num / Denom | `SUM(escalation_flag)` | `Eligible Connected Calls` | `fact_calls` | `escalation_flag` | Call | `duration >= 5` |
| **Task Completion Rate**| Num / Denom | `SUM(task_completed_flag)`| `SUM(task_started_flag)` | `fact_calls` | `task_started_flag`, `task_completed_flag` | Call | `task_started_flag=1` |
| **Resolution Rate** | Num / Denom | `SUM(resolution_flag)` | `Eligible Connected Calls` | `fact_calls` | `resolution_flag` | Call | `duration >= 5` |

### Collections (7)
| KPI | Formula / Concept | Numerator | Denominator | Source Table | Source Columns | Grain | Eligibility / Edge Cases |
|---|---|---|---|---|---|---|---|
| **Contact Rate** | Num / Denom | `COUNT(DISTINCT customer_key WHERE Connected)` | `COUNT(DISTINCT customer_key)` | `fact_calls` | `customer_key`, `connection_status` | Cust | None |
| **PTP Rate** | Num / Denom | `SUM(ptp_flag)` | `Eligible Connected Calls` | `fact_calls`, `dim_campaign`| `ptp_flag`, `campaign_type` | Call | `campaign_type='Loan Collections' AND duration>=5` |
| **Successful PTP Rate**| Num / Denom | `SUM(payment_status='Success')`| `SUM(ptp_flag)` | `fact_calls` | `ptp_flag`, `payment_status` | Call | `ptp_flag=1` |
| **Col. Conversion Rate**| Num / Denom | `COUNT(DISTINCT cust_key WHERE payment='Success')`| `COUNT(DISTINCT cust_key WHERE ptp=1)`| `fact_calls` | `customer_key`, `ptp_flag`, `payment_status`| Cust | `ptp_flag=1` |
| **PTP Amount** | Sum | `SUM(ptp_amount)` | N/A | `fact_calls` | `ptp_amount` | Call | `ptp_flag=1` |
| **Success Col. Amount**| Sum | `SUM(payment_amount)` | N/A | `fact_calls` | `payment_amount`, `payment_status`| Call | `payment_status='Success'` |
| **Outstanding Amount** | Sum | `SUM(outstanding_amount_at_call)`| N/A | `fact_calls` | `outstanding_amount_at_call` | Call | Calculated via unique max/latest per customer |

### Business Impact (3)
| KPI | Formula / Concept | Numerator | Denominator | Source Table | Source Columns | Grain | Eligibility / Edge Cases |
|---|---|---|---|---|---|---|---|
| **Est. Cost Avoided**| Calc | `Containment Count * Human Agent Cost`| N/A | `fact_calls` | `containment_flag` | Call | Uses What-If Parameter for Cost |
| **Additional Calls Auto**| Calc | `Connected Calls * Containment Imp %`| N/A | `fact_calls` | `connection_status` | Call | Uses What-If Parameter for Imp % |
| **Capacity Freed** | Calc | `Agent Hours Freed` | `Prod. Agent Hrs/Day` | `fact_calls` | `containment_flag` | Call | Unit consistent FTE calculation |

---

## 7. ML Feature Timing & Classification
**Prediction Point:** During the active call, exactly before the final escalation outcome is known.

### Derived Point-in-Time Features
These are NOT physical columns in `fact_calls`, but derived dynamically (in Python/SQL) for ML modeling using only information available prior to the prediction point:
- `call_duration_so_far`: Difference between the current turn's `timestamp` and `call_start_time`.
- `fallback_count_so_far`: Running sum of `fallback_flag` prior to the current turn.
- `turn_count_so_far`: Current `turn_number` - 1.
- `previous_call_count`: Count of calls for this `customer_id` strictly before this `call_start_time`.
- `previous_escalation_count`: Count of calls for this `customer_id` where `escalation_flag=1` strictly before this call.
- `previous_fallback_count`: Count of total fallbacks for this `customer_id` across prior calls.
- `running_confidence_score`: Average of turn-level `confidence_score` up to the current turn (distinct from the final aggregate `confidence_score` in `fact_calls`).

### ML Classification 
**Prohibited (Ground-Truth & Post-Outcome Leakage):**
- `expected_intent_key` (Ground Truth)
- `escalation_trigger_flag` (Direct outcome mapping)
- `escalation_flag` (Target itself)
- `resolution_flag`, `task_completed_flag`, `containment_flag`, `ptp_flag`
- `payment_status`, `payment_amount`, `call_status`, `hangup_reason`

**Potentially Allowed at Prediction Time:**
- `detected_intent_key`, `turn-level confidence_score`, `turn-level sentiment_score`
- `fallback_flag`, `turn_number`, `speaker`
- Point-in-time historical features (e.g. `call_duration_so_far`, `previous_escalation_count`)

---

## 8. Collections Payment Logic
Synthetic deterministic rules for MVP attribution:
- If `ptp_flag = 0`, then `ptp_amount` MUST be NULL/0.
- If `payment_status = 'Success'`, then `payment_amount` MUST be > 0.
- If `payment_status != 'Success'`, then `payment_amount` MUST be NULL/0.
- **Mandatory Synthetic Rule:** If `payment_status = 'Success'`, then `ptp_flag` MUST automatically equal `1`. (This enforces attribution strictness for the MVP).

---

## 9. Satisfaction Proxy
**Conversation Satisfaction Proxy:** 
*Project-defined analytical proxy, not survey-based CSAT and not an industry standard.*
- **Components & Normalization:**
  1. Resolution: `1` if `resolution_flag=1` else `0`. (Weight: 40%)
  2. Containment: `1` if `containment_flag=1` else `0`. (Weight: 30%)
  3. Sentiment: Normalized to 0-1 via `(sentiment_score + 1) / 2`. (Weight: 20%)
  4. Task Completion: `1` if `task_completed_flag=1` else `0`. (Weight: 10%)
- **Formula:** `(0.40 * Resolution) + (0.30 * Containment) + (0.20 * Norm_Sentiment) + (0.10 * Task_Completion)`
- **Score Range:** 0.0 to 1.0.

---

## 10. Bot Quality Score
*Project-defined analytical score, not an industry standard.*
- **Components:**
  - 30% Containment Rate
  - 25% Task Completion Rate
  - 20% Intent Recognition Accuracy
  - 15% Satisfaction Proxy
  - 10% Reliability
- **Reliability Definition:** 1 minus the percentage of calls ending in a system-fault hangup.
- **Reliability Formula:** `1 - (SUM(hangup_reason = 'System Error') / Connected Calls)`
- **Score Range:** 0.0 to 1.0.

---

## 11. Business Impact & What-If Parameters
These are Power BI What-If Parameters (project assumptions), NOT database columns:
- **Human Agent Cost per Call:** Ex: ₹50. Used to calculate *Estimated Operational Cost Avoided*.
- **Containment Improvement %:** Ex: 5%. Used to calculate *Additional Calls Automated*.
- **Average Agent Call Duration:** Ex: 300 seconds. 
- **Productive Agent Hours Per Day:** Ex: 6 hours (21600 seconds).
- **Agent Hours Freed:** `Contained Calls * Average Agent Call Duration / 3600`
- **Agent Capacity Freed (FTEs):** `Agent Hours Freed / Productive Agent Hours Per Day`

---

## 12. Synthetic Data Generation & Data Quality Rules
### Synthetic Generation Probabilities (Non-Deterministic)
- Lower confidence → higher probability of fallback.
- Higher fallback → higher probability of escalation.
- Negative sentiment → higher escalation probability.
- Higher DPD → lower PTP probability.
- Higher confidence → higher task completion probability.
- Higher task completion → higher containment probability.
*(Must include random noise, segment variation, bot-version variation, and temporal variation).*

### Data Quality Validation Rules
- **IDs:** Must be unique and non-null.
- **Dates:** `call_start_time` <= `call_end_time`.
- **Numeric:** Confidence (0 to 1), Sentiment (-1 to 1), Duration >= 0, Amounts >= 0.
- **Boolean Logic:** `containment_flag` cannot be 1 when `escalation_flag` is 1. `task_completed_flag` cannot be 1 when `task_started_flag` is 0.

---

## 13. Referential Integrity
- `dim_customer` → `fact_calls` (FK: `customer_key`)
- `dim_campaign` → `fact_calls` (FK: `campaign_key`)
- `dim_bot` → `fact_calls` (FK: `bot_key`)
- `dim_date` → `fact_calls` (FK: `date_key`)
- `dim_intent` → `fact_calls` (FK: `intent_key`)
- `fact_calls` → `fact_conversation` (FK: `call_key`)
- `dim_intent` → `fact_conversation` (FK: `expected_intent_key`)
- `dim_intent` → `fact_conversation` (FK: `detected_intent_key`)
*Invalid FKs in staging will be quarantined to `stg_error_log` tables.*

---

## 14. India Synthetic Geography
**States:** Maharashtra, Karnataka, Telangana, Andhra Pradesh, Tamil Nadu, Delhi, Haryana, Gujarat, Uttar Pradesh, West Bengal, Kerala, Rajasthan, Madhya Pradesh, Punjab.
**Cities:** Mumbai, Pune, Bengaluru, Hyderabad, Chennai, Delhi, Gurugram, Noida, Ahmedabad, Kolkata, Jaipur, Lucknow, Kochi, Vijayawada, Visakhapatnam.
*No real addresses, phone numbers, Aadhaar, PAN, or real transcripts are permitted. Geography is strictly categorical.*

---

## 15. Column Count Audit
| Layer / Table | Number of Columns Documented |
|---|---|
| `raw_customers` | 9 |
| `raw_calls` | 24 |
| `raw_conversations` | 14 |
| `stg_customers` | 10 |
| `stg_calls` | 25 |
| `stg_conversations` | 15 |
| `fact_calls` | 32 |
| `fact_conversation` | 15 |
| `dim_customer` | 12 |
| `dim_intent` | 6 |
| `dim_bot` | 7 |
| `dim_campaign` | 8 |
| `dim_date` | 12 |
| **Total Columns** | **189** |
