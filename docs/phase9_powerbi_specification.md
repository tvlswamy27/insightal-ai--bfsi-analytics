# Phase 9: Power BI Semantic Model & Implementation Plan

## 1. Power BI Semantic Model Objective
Provide a strict, interview-ready Power BI Semantic Model implementation plan connecting directly to the validated MySQL analytics layer. This semantic model utilizes a strict star schema with single-direction filtering and separated role-playing dimensions to eliminate any ambiguous relationship paths.

## 2. Table Inventory
Power BI will connect to the `insightal_analytics` database. Direct connections to raw or staging schemas are prohibited.

**Dimensions:**
- `dim_customer` (Grain: One row = one customer)
- `dim_bot` (Grain: One row = one bot version/configuration)
- `dim_campaign` (Grain: One row = one campaign)
- `dim_date` (Grain: One row = one calendar date)

**Role-playing Dimensions (Mapped from `dim_intent`):**
- `dim_intent_call` (Grain: One row = one intent; Call-level intent tracking)
- `dim_intent_expected` (Grain: One row = one intent; Conversation expected intent tracking)
- `dim_intent_detected` (Grain: One row = one intent; Conversation detected intent tracking)

*(Note: These are logical semantic-model copies created within Power BI, not new MySQL tables.)*

**Facts:**
- `fact_calls` (Grain: One row = one complete voice call)
- `fact_conversation` (Grain: One row = one conversation turn)

**Measures Table:**
- `_measures` (An empty table created inside Power BI specifically to hold all DAX measures).

## 3. Relationship Inventory
The semantic model utilizes strict 1-to-many (`1 → *`) single-direction relationships.

**Core Relationships:**
- `dim_customer[customer_key] (1) → (*) fact_calls[customer_key]`
- `dim_campaign[campaign_key] (1) → (*) fact_calls[campaign_key]`
- `dim_bot[bot_key] (1) → (*) fact_calls[bot_key]`
- `dim_date[date_key] (1) → (*) fact_calls[date_key]`
- `fact_calls[call_key] (1) → (*) fact_conversation[call_key]`

## 4. Role-playing Dimensions Relationships
To prevent ambiguous filter paths (such as `dim_intent` filtering `fact_calls` and `fact_conversation` simultaneously and creating a loop), `dim_intent` is split into distinct role-playing dimensions:

- `dim_intent_call[intent_key] (1) → (*) fact_calls[intent_key]`
- `dim_intent_expected[intent_key] (1) → (*) fact_conversation[expected_intent_key]`
- `dim_intent_detected[intent_key] (1) → (*) fact_conversation[detected_intent_key]`

**Constraint:** No bidirectional relationships, no competing active/inactive paths, and no fact-to-fact relationships (except `fact_calls → fact_conversation`).

## 5. Measure Inventory (DAX Catalog)
All measures must be created inside `_measures` using `DIVIDE` for safe division.

### A. Core Operational KPIs
- **Total Calls:** `COUNTROWS('fact_calls')`
- **Connected Calls:** `CALCULATE(COUNTROWS('fact_calls'), 'fact_calls'[connection_status] = "Connected")`
- **Connection Rate:** `DIVIDE([Connected Calls], [Total Calls])`
- **Average Call Duration:** `AVERAGE('fact_calls'[call_duration_seconds])`
- **Median Call Duration:** `MEDIAN('fact_calls'[call_duration_seconds])`
- **Average Attempts:** 
  ```dax
  AVERAGEX(
      VALUES('dim_customer'[customer_key]),
      CALCULATE(MAX('fact_calls'[attempt_number]))
  )
  ```
- **Task Completion Rate:** `DIVIDE(SUM('fact_calls'[task_completed_flag]), [Connected Calls])`
- **Resolution Rate:** `DIVIDE(SUM('fact_calls'[resolution_flag]), [Connected Calls])`
- **Containment Rate:** `DIVIDE(SUM('fact_calls'[containment_flag]), [Connected Calls])`
- **Escalation Rate:** `DIVIDE(SUM('fact_calls'[escalation_flag]), [Connected Calls])`
- **Fallback Rate:** `DIVIDE(SUM('fact_calls'[fallback_flag]), [Connected Calls])`

### B. Conversational AI KPIs
- **Intent Recognition Accuracy:** 
  ```dax
  DIVIDE(
      CALCULATE(
          COUNTROWS('fact_conversation'),
          'fact_conversation'[speaker] = "Customer",
          NOT ISBLANK('fact_conversation'[expected_intent_key]),
          NOT ISBLANK('fact_conversation'[detected_intent_key]),
          'fact_conversation'[expected_intent_key] = 'fact_conversation'[detected_intent_key]
      ),
      CALCULATE(
          COUNTROWS('fact_conversation'),
          'fact_conversation'[speaker] = "Customer",
          NOT ISBLANK('fact_conversation'[expected_intent_key]),
          NOT ISBLANK('fact_conversation'[detected_intent_key])
      )
  )
  ```
- **Average Confidence:** `AVERAGE('fact_conversation'[confidence_score])`
- **Normalized Sentiment:** `DIVIDE(AVERAGE('fact_calls'[sentiment_score]) + 1, 2)`
- **Conversation Satisfaction Proxy:** `(0.4 * [Resolution Rate]) + (0.3 * [Containment Rate]) + (0.2 * [Normalized Sentiment]) + (0.1 * [Task Completion Rate])` *(Project-defined proxy; NOT survey CSAT)*
- **Reliability:** `1 - DIVIDE(CALCULATE(COUNTROWS('fact_calls'), 'fact_calls'[hangup_reason] = "System Error"), [Connected Calls])`
- **Project-defined Bot Quality Score:** `(0.3 * [Containment Rate]) + (0.25 * [Task Completion Rate]) + (0.2 * [Intent Recognition Accuracy]) + (0.15 * [Conversation Satisfaction Proxy]) + (0.1 * [Reliability])`

### C. Collections KPIs
*All measures wrapped with `CALCULATE(..., 'dim_campaign'[campaign_type] = "Loan Collections")`*
- **Contact Rate:** `DIVIDE([Connected Collections Calls], [Total Collections Calls])`
- **PTP Rate:** `DIVIDE(SUM('fact_calls'[ptp_flag]), [Connected Collections Calls])`
- **Successful PTP Rate:** `DIVIDE(CALCULATE(COUNTROWS('fact_calls'), 'fact_calls'[payment_status] = "Success", 'fact_calls'[ptp_flag] = 1), CALCULATE(COUNTROWS('fact_calls'), 'fact_calls'[ptp_flag] = 1))`
- **Collection Conversion Rate:** `DIVIDE(CALCULATE(COUNTROWS('fact_calls'), 'fact_calls'[payment_status] = "Success"), [Connected Collections Calls])`
- **PTP Amount:** `SUM('fact_calls'[ptp_amount])`
- **Successful Collection Amount:** `CALCULATE(SUM('fact_calls'[payment_amount]), 'fact_calls'[payment_status] = "Success")`
- **Outstanding Amount:** `SUM('fact_calls'[outstanding_amount_at_call])`
- **Outstanding Collected Ratio:** `DIVIDE([Successful Collection Amount], [Outstanding Amount])`

## 6. What-If Parameters & Scenario Measures

**Parameters:**
1. `WhatIf_CostPerCall` (Default `₹50`)
2. `WhatIf_ContainmentImprovement` (Default `5%`)
3. `WhatIf_AgentCallDuration` (Default `300 seconds`)
4. `WhatIf_ProductiveHours` (Default `6 hours`)

**Actual vs Scenario Measures:**
- **Actual Contained Calls:** `SUM('fact_calls'[containment_flag])`
- **Actual Agent Calls Avoided:** `[Actual Contained Calls]`
- **Scenario Containment Rate:** `[Containment Rate] + [WhatIf_ContainmentImprovement]`
- **Scenario Additional Contained Calls:** `[Connected Calls] * [WhatIf_ContainmentImprovement]`
- **Scenario Total Contained Calls:** `[Actual Contained Calls] + [Scenario Additional Contained Calls]`
- **Scenario Additional Agent Hours Freed:** `DIVIDE([Scenario Additional Contained Calls] * [WhatIf_AgentCallDuration], 3600)`
- **Scenario Additional Cost Avoided:** `[Scenario Additional Contained Calls] * [WhatIf_CostPerCall]`

*(Visuals must clearly label scenario outputs as hypothetical.)*

## 7. Validation Checklist (Baseline vs Power BI)
Values must reconcile with the clean Phase 7 SQL baseline (subject to identical filter context):
- [ ] Total Calls: `9,885`
- [ ] Connected Calls: `6,183`
- [ ] Connection Rate: `62.55%`
- [ ] Containment Rate: `52.05%`
- [ ] Resolution Rate: `56.17%`
- [ ] Intent Recognition Accuracy: `83.39%`
- [ ] Successful PTP Rate: `62.92%`
- [ ] Successful Collection Amount: `₹2,239,430.79`
- [ ] Estimated Cost Avoided (Actual base): `₹160,900`

## 8. Known Limitations
- Descriptive Associations: Dashboards mapping escalation to sentiments are correlational and do not prove causation.
- Synthetic Data: Data is fully anonymized/synthetic for portfolio demonstration purposes.
