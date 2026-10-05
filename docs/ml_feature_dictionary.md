# ML Feature Dictionary

This dictionary defines the exact point-in-time features to be extracted for the Escalation Prediction ML model. The prediction snapshot is anchored at the **3rd customer turn** (`prediction_timestamp`). All feature calculations must remain strictly point-in-time as of this timestamp. 

## 1. Conversation Context (Point-in-Time: Turn 3)
Features calculated dynamically up to and including the 3rd customer turn.

| Feature Name | Source Table | Source Column | Transformation | Prediction-Time Availability | Leakage Status | Rationale |
|---|---|---|---|---|---|---|
| `detected_intent_at_t3` | `fact_conversation` | `detected_intent_key` | Last non-null detected intent key at or before Turn 3 | Point-in-Time (Turn 3) | Clean | AI's understanding of the user's intent by T3 heavily influences routing success. |
| `running_confidence_t3` | `fact_conversation` | `confidence_score` | Mean of confidence scores for Customer turns 1, 2, and 3 | Point-in-Time (Turn 3) | Clean | Lower cumulative confidence suggests the bot is struggling early in the call. |
| `fallback_count_t3` | `fact_conversation` | `fallback_flag` | Sum of `fallback_flag` across turns 1, 2, and 3 | Point-in-Time (Turn 3) | Clean | Multiple early fallbacks strongly correlate with frustration and escalation risk. |
| `current_sentiment_t3` | `fact_conversation` | `sentiment` | The categorical sentiment string from exactly Turn 3 | Point-in-Time (Turn 3) | Clean | Captures the user's immediate mood at the snapshot boundary. |
| `running_sentiment_score_t3`| `fact_conversation`| `sentiment_score` | Mean of sentiment scores for turns 1, 2, and 3 | Point-in-Time (Turn 3) | Clean | Measures compounding positive or negative emotional trajectory. |
| `call_duration_so_far_t3` | `fact_calls`, `fact_conversation` | `timestamp`, `call_start_time` | Duration in seconds from `call_start_time` to the timestamp of Turn 3 | Point-in-Time (Turn 3) | Clean | Captures early interaction velocity (e.g., long pauses or swift exchanges). |

## 2. Call Metadata (Historical Pre-Call)
Features established exactly when the call was initiated.

| Feature Name | Source Table | Source Column | Transformation | Prediction-Time Availability | Leakage Status | Rationale |
|---|---|---|---|---|---|---|
| `bot_version` | `dim_bot` | `bot_version` | Direct extraction | Historical Pre-Call | Clean | Captures systemic performance differences between AI releases. |
| `language` | `dim_bot` | `language` | Direct extraction | Historical Pre-Call | Clean | Accounts for NLP model accuracy variations across languages. |
| `campaign_type` | `dim_campaign` | `campaign_type` | Direct extraction | Historical Pre-Call | Clean | Different campaigns have different intrinsic escalation baselines. |
| `attempt_number` | `fact_calls` | `attempt_number` | Direct extraction | Historical Pre-Call | Clean | Higher attempt counts may indicate an annoyed or harder-to-reach customer. |

## 3. Customer Historical Profile (Historical Pre-Call)
Features calculated using ONLY interactions that completely ended prior to the current `call_start_time`.

| Feature Name | Source Table | Source Column | Transformation | Prediction-Time Availability | Leakage Status | Rationale |
|---|---|---|---|---|---|---|
| `previous_call_count` | `fact_calls` | `call_id` | Count of prior calls for this `customer_key` where `call_end_time < current_call_start_time` | Historical Pre-Call | Clean | Frequent callers may have unresolved complex issues. |
| `previous_escalation_count`| `fact_calls` | `escalation_flag` | Sum of escalations for prior calls where `call_end_time < current_call_start_time` | Historical Pre-Call | Clean | Customers with a history of escalating are likely to escalate again. |
| `previous_fallback_count` | `fact_calls`, `fact_conversation` | `fallback_flag` | Total fallbacks experienced by `customer_key` in all strictly prior calls | Historical Pre-Call | Clean | Measures historical friction experienced by the customer. |
| `customer_segment` | `dim_customer` | `customer_segment` | Direct extraction | Historical Pre-Call | Clean | High-value segments may have lower thresholds for patience. |
| `age_group` | `dim_customer` | `age_group` | Direct extraction | Historical Pre-Call | Clean | Demographic indicator for tech fluency or preference for human agents. |
| `loan_type` | `dim_customer` | `loan_type` | Direct extraction | Historical Pre-Call | Clean | Different product portfolios carry varying degrees of anxiety and complexity. |

## 4. Collections Context (Historical Pre-Call)
Features detailing the customer's account state at the exact moment the call was placed.

| Feature Name | Source Table | Source Column | Transformation | Prediction-Time Availability | Leakage Status | Rationale |
|---|---|---|---|---|---|---|
| `days_past_due_at_call` | `fact_calls` | `days_past_due_at_call` | Direct extraction | Historical Pre-Call | Clean | Delinquency severity heavily impacts the tone of the conversation. |
| `dpd_bucket_at_call` | `fact_calls` | `dpd_bucket_at_call` | Direct extraction | Historical Pre-Call | Clean | Categorical representation of delinquency. |
| `risk_segment_at_call` | `fact_calls` | `risk_segment_at_call` | Direct extraction | Historical Pre-Call | Clean | Operational risk classification at the time of outreach. |
| `outstanding_amount_at_call`| `fact_calls` | `outstanding_amount_at_call`| Direct extraction | Historical Pre-Call | Clean | Larger debt amounts generally lead to more complicated negotiation. |

## 5. Prohibited Features (Strict Target Leakage)
These features MUST NOT be included in the ML dataset. The leakage audit will explicitly scan for their absence.

| Feature Name | Leakage Reason |
|---|---|
| `escalation_after_t3` | **TARGET VARIABLE** |
| `escalation_flag` | Final outcome flag; leaks target. |
| `escalation_trigger_flag` | Used ONLY to construct the target label; must NEVER appear in the feature matrix. |
| `expected_intent_key` | Ground truth; not known by the AI at inference time. |
| `resolution_flag` | Outcome variable; determined post-call. |
| `task_completed_flag` | Outcome variable; determined post-call. |
| `containment_flag` | Outcome variable (inverse of escalation). |
| `ptp_flag` | Outcome variable; determined post-call. |
| `payment_status` | Downstream consequence of the call. |
| `payment_amount` | Downstream consequence of the call. |
| `call_status` | Post-call final disposition. |
| `hangup_reason` | Post-call termination cause. |
| `call_duration_seconds` | Final call duration. Replaced by `call_duration_so_far_t3`. |
| `final_confidence_score` | Final call aggregate. Replaced by `running_confidence_t3`. |
