# Phase 13B — PBIP Verification

## 1. Overall Status
PASS WITH ISSUES

## 2. PBIP Location
- **Path:** `C:\Users\TVL SWAMY\Desktop\DA_1\Insightal_AI_BFSI_Analytics_Final_4Page_Polished`
- **PBIP File:** `Insightal_AI_BFSI_Analytics.pbip`
- **Report Folder:** `Insightal_AI_BFSI_Analytics.Report`
- **SemanticModel Folder:** `Insightal_AI_BFSI_Analytics.SemanticModel`
- **Definition Structure:** Uses the modern PBIR definition structure (`definition/pages/` containing individual `page.json` and `visuals/` subdirectories).

## 3. Page Count
Exactly 4 visible pages were found in the PBIP definitions.

## 4. Page Verification

| Page | Found | Visible | Status |
|---|---|---|---|
| Executive Overview | Yes | Yes (FitToPage) | PASS |
| Conversational AI & Customer Journey | Yes | Yes (FitToPage) | PASS |
| Collections Performance | Yes | Yes (FitToPage) | PASS |
| Business Impact & Escalation | Yes | Yes (FitToPage) | PASS |

- *Customer Insights* and *Scenario Analysis* pages are completely removed.

## 5. Canvas Verification
- **Size:** 1280 × 720
- **Status:** PASS (Verified in `page.json` width/height for all 4 pages).

## 6. Semantic Model Verification
All expected core tables and role-playing dimensions are present in `definition/tables/*.tmdl`:
- `insightal_analytics dim_customer`
- `insightal_analytics dim_intent`
- `insightal_analytics dim_bot`
- `insightal_analytics dim_campaign`
- `insightal_analytics dim_date`
- `insightal_analytics fact_calls`
- `insightal_analytics fact_conversation`
- `dim_intent_call`, `dim_intent_expected`, `dim_intent_detected`

## 7. Relationship Verification
All relationships are correctly defined as 1-to-many, single-direction, and active (`relationships.tmdl`):
- `fact_calls[bot_key]` → `dim_bot[bot_key]`
- `fact_calls[campaign_key]` → `dim_campaign[campaign_key]`
- `fact_calls[customer_key]` → `dim_customer[customer_key]`
- `fact_calls[date_key]` → `dim_date[date_key]`
- `fact_calls[intent_key]` → `dim_intent_call[intent_key]`
- `fact_conversation[expected_intent_key]` → `dim_intent_expected[intent_key]`
- `fact_conversation[detected_intent_key]` → `dim_intent_detected[intent_key]`
- `fact_conversation[call_key]` → `fact_calls[call_key]`
- **Status:** PASS (No ambiguous paths, no `LocalDateTable` auto-date relationships).

## 8. Measure Verification
Core operational and Conversational AI measures are fully implemented in `_measures.tmdl`, including Total Calls, Connected Calls, Intent Recognition Accuracy, Sentiment, Reliability, and Project-defined Bot Quality Score. 

## 9. KPI Verification
The semantic model provides the DAX logic capable of computing the target KPIs (6,183 connected calls out of 9,885 total). The measure expressions perfectly align with the expected final definitions (e.g., Containment Rate = Contained / Connected).

## 10. Collections Verification
- **Collection Conversion Rate DAX:** Successfully updated to use distinct customers: `DIVIDE(CALCULATE(DISTINCTCOUNT('insightal_analytics fact_calls'[customer_key]), 'insightal_analytics fact_calls'[ptp_flag] = TRUE(), 'insightal_analytics fact_calls'[payment_status] = "Success"), CALCULATE(DISTINCTCOUNT('insightal_analytics fact_calls'[customer_key]), 'insightal_analytics fact_calls'[ptp_flag] = TRUE()))`.
- **Status:** PASS.

## 11. Outstanding Amount Verification
- **DAX Found:** `CALCULATE(SUM('insightal_analytics fact_calls'[outstanding_amount_at_call]), 'insightal_analytics dim_campaign'[campaign_type] = "Loan Collections")`
- **Status:** OLD / FLAWED DAX STILL PRESENT. The measure incorrectly uses `SUM` which double-counts outstanding amounts for repeat callers, rather than using a unique/latest calculation.

## 12. Visual Reference Verification
All scanned visuals reference valid existing tables (`insightal_analytics fact_calls`, `_measures`, `dim_intent_call`, etc.). No missing fields, deleted dimensions, or invalid measures were found.

## 13. Stale Content Verification
- Old page IDs and names (Customer Insights, Scenario Analysis) are entirely absent from the `pages.json` array and directory structure.
- **Status:** PASS.

## 14. PBIP Integrity
- Valid JSON and TMDL syntax.
- Modern PBIR schema properly adhered to.
- No missing SemanticModel or Report folders.
- **Status:** PASS.

## 15. Issues Found

**HIGH:**
- **Flawed DAX:** Outstanding Amount still relies on a simple `SUM()`, preventing accurate portfolio risk sizing.

## 16. Recommended Next Action
Since this is an audit step, no actions have been taken. The project owner should manually update the `Outstanding Amount` DAX logic within Power BI Desktop to use a `LASTNONBLANK` or `MAX` approach by customer to resolve the double-counting, then re-save the PBIP.
