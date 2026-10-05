# Phase 9: Power BI Semantic Model Implementation

## 1. Implementation Status
**STATUS:** PENDING MANUAL EXECUTION  
**POWER BI DESKTOP EXECUTION:** NOT EXECUTED  
*(Note: As Power BI Desktop cannot be controlled in this automated environment, the implementation steps below must be manually executed by a BI Developer. No `.pbix` file has been automatically generated.)*

## 2. Source Tables
Connect to MySQL (`localhost:3306`, database `insightal_analytics`) and import the following seven tables:
- `dim_customer`
- `dim_intent`
- `dim_bot`
- `dim_campaign`
- `dim_date`
- `fact_calls`
- `fact_conversation`

*(Do not connect to raw or staging schemas.)*

## 3. Role-playing Dimensions
In Power Query or the Model View, duplicate `dim_intent` three times to create these role-playing dimensions (do NOT create new MySQL tables):
- `dim_intent_call`
- `dim_intent_expected`
- `dim_intent_detected`

## 4. Relationship Matrix
Establish the following exact 1-to-many, single-direction, active relationships. Ensure no bidirectional cross-filtering is enabled, and no ambiguous filter paths remain.

| From (1 Side) | To (* Side) | Active |
| ------------- | ----------- | ------ |
| `dim_customer[customer_key]` | `fact_calls[customer_key]` | Yes |
| `dim_campaign[campaign_key]` | `fact_calls[campaign_key]` | Yes |
| `dim_bot[bot_key]` | `fact_calls[bot_key]` | Yes |
| `dim_date[date_key]` | `fact_calls[date_key]` | Yes |
| `dim_intent_call[intent_key]` | `fact_calls[intent_key]` | Yes |
| `fact_calls[call_key]` | `fact_conversation[call_key]` | Yes |
| `dim_intent_expected[intent_key]` | `fact_conversation[expected_intent_key]` | Yes |
| `dim_intent_detected[intent_key]` | `fact_conversation[detected_intent_key]` | Yes |

## 5. Measures Created
Create a dedicated empty table named `_measures` and implement the following DAX calculations:

### Operational
- **Total Calls** = `COUNTROWS('fact_calls')`
- **Connected Calls** = `CALCULATE(COUNTROWS('fact_calls'), 'fact_calls'[connection_status] = "Connected")`
- **Connection Rate** = `DIVIDE([Connected Calls], [Total Calls])`
- **Average Call Duration** = `AVERAGE('fact_calls'[call_duration_seconds])`
- **Median Call Duration** = `MEDIAN('fact_calls'[call_duration_seconds])`
- **Average Attempts** = `AVERAGEX(VALUES('dim_customer'[customer_key]), CALCULATE(MAX('fact_calls'[attempt_number])))`
- **Task Completion Rate** = `DIVIDE(SUM('fact_calls'[task_completed_flag]), [Connected Calls])`
- **Resolution Rate** = `DIVIDE(SUM('fact_calls'[resolution_flag]), [Connected Calls])`
- **Containment Rate** = `DIVIDE(SUM('fact_calls'[containment_flag]), [Connected Calls])`
- **Escalation Rate** = `DIVIDE(SUM('fact_calls'[escalation_flag]), [Connected Calls])`
- **Fallback Rate** = `DIVIDE(SUM('fact_calls'[fallback_flag]), [Connected Calls])`

### Conversational AI
- **Intent Recognition Accuracy** = 
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
- **Average Confidence** = `AVERAGE('fact_conversation'[confidence_score])`
- **Normalized Sentiment** = `DIVIDE(AVERAGE('fact_calls'[sentiment_score]) + 1, 2)`
- **Conversation Satisfaction Proxy** = `(0.4 * [Resolution Rate]) + (0.3 * [Containment Rate]) + (0.2 * [Normalized Sentiment]) + (0.1 * [Task Completion Rate])`
- **Reliability** = `1 - DIVIDE(CALCULATE(COUNTROWS('fact_calls'), 'fact_calls'[hangup_reason] = "System Error"), [Connected Calls])`
- **Project-defined Bot Quality Score** = `(0.3 * [Containment Rate]) + (0.25 * [Task Completion Rate]) + (0.2 * [Intent Recognition Accuracy]) + (0.15 * [Conversation Satisfaction Proxy]) + (0.1 * [Reliability])`

### Collections
- **Total Collections Calls** = `CALCULATE([Total Calls], 'dim_campaign'[campaign_type] = "Loan Collections")`
- **Connected Collections Calls** = `CALCULATE([Connected Calls], 'dim_campaign'[campaign_type] = "Loan Collections")`
- **Contact Rate** = `DIVIDE([Connected Collections Calls], [Total Collections Calls])`
- **PTP Rate** = `DIVIDE(CALCULATE(SUM('fact_calls'[ptp_flag]), 'dim_campaign'[campaign_type] = "Loan Collections"), [Connected Collections Calls])`
- **Successful PTP Rate** = `DIVIDE(CALCULATE(COUNTROWS('fact_calls'), 'fact_calls'[payment_status] = "Success", 'fact_calls'[ptp_flag] = 1, 'dim_campaign'[campaign_type] = "Loan Collections"), CALCULATE(COUNTROWS('fact_calls'), 'fact_calls'[ptp_flag] = 1, 'dim_campaign'[campaign_type] = "Loan Collections"))`
- **Collection Conversion Rate** = `DIVIDE(CALCULATE(COUNTROWS('fact_calls'), 'fact_calls'[payment_status] = "Success", 'dim_campaign'[campaign_type] = "Loan Collections"), [Connected Collections Calls])`
- **PTP Amount** = `CALCULATE(SUM('fact_calls'[ptp_amount]), 'dim_campaign'[campaign_type] = "Loan Collections")`
- **Successful Collection Amount** = `CALCULATE(SUM('fact_calls'[payment_amount]), 'fact_calls'[payment_status] = "Success", 'dim_campaign'[campaign_type] = "Loan Collections")`
- **Outstanding Amount** =
  ```dax
  CALCULATE(
      SUMX(
          VALUES('fact_calls'[customer_key]),
          VAR MaxTime =
              CALCULATE(
                  MAX('fact_calls'[call_start_time])
              )
          RETURN
              CALCULATE(
                  MAX('fact_calls'[outstanding_amount_at_call]),
                  'fact_calls'[call_start_time] = MaxTime
              )
      ),
      'fact_calls'[connection_status] = "Connected",
      'dim_campaign'[campaign_type] = "Loan Collections"
  )
  ```
- **Outstanding Collected Ratio** = `DIVIDE([Successful Collection Amount], [Outstanding Amount])`
  *(Validated Result - Outstanding Amount: ₹24,379,952.04, Outstanding Collected Ratio: 9.19%)*

## 6. What-If Parameters & Scenario Measures

**Parameters (To create via Modeling > New Parameter):**
- `WhatIf_CostPerCall` (Default `50`)
- `WhatIf_ContainmentImprovement` (Default `0.05`)
- `WhatIf_AgentCallDuration` (Default `300`)
- `WhatIf_ProductiveHours` (Default `6`)

**Actual vs Scenario Measures:**
- **Actual Contained Calls** = `SUM('fact_calls'[containment_flag])`
- **Actual Agent Calls Avoided** = `[Actual Contained Calls]`
- **Scenario Containment Rate** = `[Containment Rate] + [WhatIf_ContainmentImprovement Value]`
- **Scenario Additional Contained Calls** = `[Connected Calls] * [WhatIf_ContainmentImprovement Value]`
- **Scenario Total Contained Calls** = `[Actual Contained Calls] + [Scenario Additional Contained Calls]`
- **Scenario Additional Agent Hours Freed** = `DIVIDE([Scenario Additional Contained Calls] * [WhatIf_AgentCallDuration Value], 3600)`
- **Scenario Additional Cost Avoided** = `[Scenario Additional Contained Calls] * [WhatIf_CostPerCall Value]`

## 7. Validation Matrix
**STATUS:** NOT EXECUTED

| KPI | Phase 7 Baseline | Actual Power BI | Discrepancy |
| --- | ----------------- | --------------- | ----------- |
| Total Calls | 9,885 | PENDING | PENDING |
| Connected Calls | 6,183 | PENDING | PENDING |
| Connection Rate | 62.55% | PENDING | PENDING |
| Containment Rate | 52.05% | PENDING | PENDING |
| Resolution Rate | 56.17% | PENDING | PENDING |
| Intent Recognition Accuracy | 83.39% | PENDING | PENDING |
| Successful PTP Rate | 62.92% | PENDING | PENDING |
| Successful Collection Amount | ₹2,239,430.79 | PENDING | PENDING |
| Estimated Cost Avoided | ₹160,900 | PENDING | PENDING |

## 8. Discrepancies
None recorded (Execution Pending).

## 9. Manual Power BI Steps Required
1. Open Power BI Desktop.
2. Get Data > MySQL database (localhost:3306).
3. Import the 7 approved tables.
4. Create the role-playing dimensions in Model view.
5. Establish relationships as per Section 4.
6. Create `_measures` table.
7. Paste all DAX formulas from Section 5 & 6.
8. Create What-If parameters.
9. Cross-check KPI values against the baseline in Section 7.

## 10. Known Limitations
- Power BI Desktop cannot be fully automated from this script environment.
- Descriptive Associations: Correlational dashboards do not prove causation.
- Synthetic Data: Data is fully anonymized.
