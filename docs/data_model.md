# Analytical Data Model
**Project:** Insightal AI — Conversational AI & BFSI Voice Analytics Platform

## 1. Grain Definitions
| Table | Grain | Description |
|---|---|---|
| `fact_calls` | **Call Level** | One row represents one complete voice call interaction from start to disconnect. |
| `fact_conversation` | **Conversation Turn** | One row represents a single utterance (either by bot or customer) within a call. |

---

## 2. Fact Tables

### 2.1 `fact_calls`
**Grain:** Call Level
**Description:** Tracks overall call connectivity, duration, AI containment, task completion, and collection outcomes. 
**Collections Attribution Assumption:** A payment outcome is attributed to the call/campaign interaction represented by the call record, and the synthetic dataset will enforce at most one attributed payment outcome per call. *Note: This is a synthetic-project assumption rather than a universal BFSI accounting rule.*

| Column | Data Type | Nullable | Description / Business Meaning | Type |
|---|---|---|---|---|
| `call_key` | BIGINT (PK) | No | Surrogate key for the call. | Derived |
| `call_id` | VARCHAR(50) | No | Natural identifier for the call. | Source |
| `customer_key` | INT (FK) | No | Links to `dim_customer`. | Derived |
| `campaign_key` | INT (FK) | No | Links to `dim_campaign`. | Derived |
| `bot_key` | INT (FK) | No | Links to `dim_bot`. | Derived |
| `date_key` | INT (FK) | No | Links to `dim_date` (Format: YYYYMMDD). | Derived |
| `intent_key` | INT (FK) | Yes | Primary intent of the call (Links to `dim_intent`). | Derived |
| `call_start_time` | DATETIME | No | When the call connected/started. | Source |
| `call_end_time` | DATETIME | No | When the call terminated. | Source |
| `call_duration_seconds` | INT | No | Total duration. | Derived |
| `call_status` | VARCHAR(20) | No | E.g., 'Completed', 'Dropped', 'Failed'. | Source |
| `connection_status` | VARCHAR(20) | No | E.g., 'Connected', 'Voicemail', 'No Answer'. | Source |
| `hangup_reason` | VARCHAR(50) | Yes | E.g., 'Customer Hung Up', 'System Error', 'Normal'. | Source |
| `attempt_number` | INT | No | Which attempt this is for the customer/campaign. | Source |
| `confidence_score` | DECIMAL(5,4)| Yes | Average or Final confidence score of the call. | Derived |
| `outstanding_amount_at_call`| DECIMAL(12,2)| Yes | Customer's outstanding amount at the time of the call. | Source |
| `days_past_due_at_call` | INT | Yes | Customer's DPD at the time of the call. | Source |
| `dpd_bucket_at_call` | VARCHAR(20) | Yes | E.g., '0-30', '31-60', '61-90', '90+'. | Derived |
| `risk_segment_at_call` | VARCHAR(20) | Yes | E.g., 'High Risk', 'Medium Risk', 'Low Risk'. | Derived |
| `identity_verified_flag`| BOOLEAN | No | 1 if customer identity was verified, 0 otherwise. | Source |
| `task_started_flag` | BOOLEAN | No | 1 if the bot began the primary task. | Source |
| `task_completed_flag`| BOOLEAN | No | 1 if the primary task was completed. | Source |
| `resolution_flag` | BOOLEAN | No | 1 if the overall call was successfully resolved. | Source |
| `fallback_flag` | BOOLEAN | No | 1 if any fallback occurred during the call. | Derived |
| `escalation_flag` | BOOLEAN | No | 1 if the call was escalated to a human. | Source |
| `containment_flag` | BOOLEAN | No | 1 if successfully AI-contained. | Derived |
| `sentiment` | VARCHAR(20) | Yes | E.g., 'Positive', 'Neutral', 'Negative'. | Derived |
| `sentiment_score` | DECIMAL(5,4)| Yes | Ranging from -1 (Negative) to 1 (Positive). | Derived |
| `ptp_flag` | BOOLEAN | No | 1 if Promise to Pay was secured. | Source |
| `ptp_amount` | DECIMAL(10,2)| Yes | Amount promised. | Source |
| `payment_status` | VARCHAR(20) | Yes | E.g., 'Success', 'Failed', 'Pending'. | Source |
| `payment_amount` | DECIMAL(10,2)| Yes | Actual amount paid. | Source |

### 2.2 `fact_conversation`
**Grain:** Conversation Turn Level
**Description:** Tracks granular back-and-forth dialogue, turn-level intent recognition, and fallbacks. 
**Intent Recognition Ground Truth:** Intent Recognition Accuracy is calculated **only** on eligible customer utterance turns where a ground-truth expected intent exists and the AI produced a detected intent. 
*Denominator rule:* `speaker = 'Customer' AND expected_intent_key IS NOT NULL AND detected_intent_key IS NOT NULL`. (Do not automatically include Bot turns). `expected_intent_key` represents the synthetic ground truth, while `detected_intent_key` represents the AI's prediction.

| Column | Data Type | Nullable | Description / Business Meaning | Type |
|---|---|---|---|---|
| `turn_key` | BIGINT (PK) | No | Surrogate key for the unique turn. | Derived |
| `turn_id` | VARCHAR(50) | No | Natural unique identifier for the turn. | Source |
| `conversation_id` | VARCHAR(50) | No | Identifier for the overarching conversation/call. | Source |
| `call_key` | BIGINT (FK) | No | Links to `fact_calls`. | Derived |
| `turn_number` | INT | No | Sequential turn number within the call (1, 2, 3...). | Source |
| `speaker` | VARCHAR(10) | No | 'Customer' or 'Bot'. | Source |
| `timestamp` | DATETIME | No | Exact time of the utterance. | Source |
| `utterance` | TEXT | Yes | The transcribed text (synthetic). | Source |
| `expected_intent_key`| INT (FK) | Yes | The ground-truth intent (Links to `dim_intent`). | Source |
| `detected_intent_key`| INT (FK) | Yes | The intent the AI actually detected (Links to `dim_intent`). | Source |
| `confidence_score` | DECIMAL(5,4)| Yes | AI confidence in the detected intent (for Bot turns/evaluations). | Source |
| `sentiment` | VARCHAR(20) | Yes | Turn-level sentiment. | Source |
| `sentiment_score` | DECIMAL(5,4)| Yes | Turn-level numerical sentiment. | Source |
| `fallback_flag` | BOOLEAN | No | 1 if the bot failed to understand and triggered a fallback. | Source |
| `escalation_trigger_flag`| BOOLEAN| No | 1 if this specific turn triggered human escalation. | Source |

---

## 3. Dimension Tables

### 3.1 `dim_customer`
| Column | Data Type | Description |
|---|---|---|
| `customer_key` | INT (PK) | Surrogate key. |
| `customer_id` | VARCHAR(50) | Natural ID (Synthetic). |
| `age` | INT | Customer age. |
| `age_group` | VARCHAR(20) | E.g., '18-25', '26-35'. |
| `gender` | VARCHAR(10) | E.g., 'M', 'F', 'Other'. |
| `city` | VARCHAR(50) | Synthetic India City (e.g., 'Mumbai'). |
| `state` | VARCHAR(50) | Synthetic India State (e.g., 'Maharashtra'). |
| `region` | VARCHAR(20) | E.g., 'North', 'South', 'West', 'East'. |
| `customer_type` | VARCHAR(20) | E.g., 'Retail', 'Corporate'. |
| `customer_segment`| VARCHAR(20) | E.g., 'High Value', 'Standard'. |
| `loan_type` | VARCHAR(30) | E.g., 'Personal Loan', 'Auto Loan', 'Home Loan'. |
| `customer_since_date`| DATE | Date customer joined. |

### 3.2 `dim_intent`
| Column | Data Type | Description |
|---|---|---|
| `intent_key` | INT (PK) | Surrogate key. |
| `intent_id` | VARCHAR(50) | Natural ID. |
| `intent_name` | VARCHAR(50) | E.g., 'Promise to Pay', 'EMI Query'. |
| `intent_category` | VARCHAR(50) | E.g., 'Collections', 'Servicing'. |
| `business_function`| VARCHAR(50) | E.g., 'Debt Recovery', 'Customer Support'. |
| `expected_task` | VARCHAR(50) | E.g., 'Capture Payment Date'. |

### 3.3 `dim_bot`
| Column | Data Type | Description |
|---|---|---|
| `bot_key` | INT (PK) | Surrogate key. |
| `bot_id` | VARCHAR(50) | Natural ID. |
| `bot_name` | VARCHAR(50) | E.g., 'Insightal Voice'. |
| `bot_version` | VARCHAR(20) | E.g., 'v1.0', 'v2.1'. |
| `language` | VARCHAR(20) | E.g., 'English', 'Hindi', 'Hinglish'. |
| `model_type` | VARCHAR(30) | E.g., 'Generative', 'NLU-Rules'. |
| `deployment_date`| DATE | When version went live. |

### 3.4 `dim_campaign`
| Column | Data Type | Description |
|---|---|---|
| `campaign_key` | INT (PK) | Surrogate key. |
| `campaign_id` | VARCHAR(50) | Natural ID. |
| `campaign_name` | VARCHAR(100)| E.g., 'Q3 Collections High Risk'. |
| `campaign_type` | VARCHAR(50) | E.g., 'Loan Collections', 'EMI Reminder'. |
| `business_unit` | VARCHAR(50) | E.g., 'Retail Banking', 'Credit Cards'. |
| `start_date` | DATE | Campaign start. |
| `end_date` | DATE | Campaign end. |
| `target_segment` | VARCHAR(50) | E.g., 'DPD 60-90'. |

### 3.5 `dim_date`
*Uses Indian Financial Year (April - March)*
| Column | Data Type | Description |
|---|---|---|
| `date_key` | INT (PK) | Format YYYYMMDD. |
| `date` | DATE | Actual date. |
| `day` | INT | 1-31. |
| `day_name` | VARCHAR(15) | 'Monday', etc. |
| `week` | INT | 1-52. |
| `month` | INT | 1-12. |
| `month_name` | VARCHAR(15) | 'January', etc. |
| `quarter` | INT | 1-4. |
| `year` | INT | Calendar Year. |
| `financial_year` | VARCHAR(10) | E.g., 'FY24-25'. |
| `is_weekend` | BOOLEAN | 1 if Sat/Sun. |

---

## 4. Relationships
- `dim_customer` (1) to (M) `fact_calls` (via `customer_key`)
- `dim_campaign` (1) to (M) `fact_calls` (via `campaign_key`)
- `dim_bot` (1) to (M) `fact_calls` (via `bot_key`)
- `dim_date` (1) to (M) `fact_calls` (via `date_key`)
- `dim_intent` (1) to (M) `fact_calls` (via `intent_key` - represents the primary intent of the call)
- `fact_calls` (1) to (M) `fact_conversation` (via `call_key`)
- `dim_intent` (1) to (M) `fact_conversation` (via `expected_intent_key` and `detected_intent_key`)

*Referential integrity will be maintained strictly during ETL into the analytics schema.*

---

## 5. Indexing Strategy
To support 100K-500K scale efficiently in MySQL, we will use a refined indexing strategy avoiding unnecessary single-column boolean indexes:

**Primary Keys & Foreign Keys:**
- B-Tree indexes on all primary keys (`call_key`, `turn_key`, etc.) and all foreign keys (`customer_key`, `campaign_key`, `bot_key`, `date_key`, `call_key`, `expected_intent_key`, `detected_intent_key`).

**Composite Indexes (Justified by Queries):**
- `(date_key, escalation_flag)`: Highly useful for time-series filtering on escalations in Power BI.
- `(bot_key, date_key)`: Useful for querying bot performance over time.
- `(campaign_key, date_key)`: Useful for time-bound campaign reporting.
- `(intent_key, date_key)`: Useful for intent volume tracking over time.

*Justification:* Fact table foreign keys are almost always used in JOINs or WHERE clauses. Composite indexes grouping dimensions and time will dramatically speed up star-schema aggregations and dashboard filtering without the overhead of indexing every individual boolean flag.

---

## 6. Call <-> Conversation Relationship
The relationship is defined explicitly through the 1:M link from `fact_calls.call_key` to `fact_conversation.call_key`.
- **Avoids Duplication:** Overall call metrics (e.g., duration, final PTP amount, containment) live ONLY in `fact_calls`. They are not repeated across turns.
- **Power BI Implementation Note:** Relationships between `fact_calls` and `fact_conversation` should be **single-direction**. Unrestricted bidirectional filtering is prohibited to avoid ambiguous filter paths.

---

## 7. Collections Model Integration
No separate fact table is required for Collections. The Collections process (PTP, Amount, Payment) is inherently a 1-to-1 outcome of a specific Call.
- We utilize fields in `fact_calls` (`outstanding_amount_at_call`, `days_past_due_at_call`, `risk_segment_at_call`, `ptp_flag`, `payment_status`, `payment_amount`) to handle the complete collections funnel exactly as it stood at the time of the call.
- Adding a separate `fact_collections` would unnecessarily complicate the Power BI model when the grain (the Call) is exactly the same.
