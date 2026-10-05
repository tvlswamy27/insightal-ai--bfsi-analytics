# Page 1: Executive Overview (Implementation Specification)

**Status:** NOT EXECUTED (Power BI visual layouts cannot be programmatically generated via the TOM API or MCP. This document serves as the implementation guide for a developer to build the visuals in Power BI Desktop manually).

## 1. Page Header
- **Title:** Insightal AI — Executive Overview
- **Subtitle:** Conversational AI & BFSI Voice Analytics Platform
- **Disclosure text (Small, bottom/right of header):** "Synthetic / anonymized project dataset"

## 2. Top KPI Cards
Create four consistent KPI cards horizontally:
1. **Total Calls:** `[Total Calls]` (Expected: 9,885)
2. **Connected Calls:** `[Connected Calls]` (Expected: 6,183)
3. **Connection Rate:** `[Connection Rate]` (Expected: 62.55%)
4. **Average Call Duration:** `[Average Call Duration]` (Expected: 36.56 seconds)

## 3. Operational Trend
- **Visual Type:** Line Chart
- **Title:** Call Volume Trend
- **X-Axis:** `dim_date[date]`
- **Y-Axis (Values):** `[Total Calls]`

## 4. AI Performance
- **Visual Type:** Clustered Bar or Column Chart
- **Title:** Conversational AI Performance
- **Values (Metrics compared):**
  - `[Intent Recognition Accuracy]`
  - `[Task Completion Rate]`
  - `[Containment Rate]`
  - `[Resolution Rate]`
  - `[Escalation Rate]`
  - `[Fallback Rate]`
- **Formatting:** Use percentage formatting. Do not add rank-based conditional formatting.

## 5. Conversation Quality
- **Visual Type:** Multi-row Card or individual KPI Cards
- **Fields:**
  - `[Intent Recognition Accuracy]` (Expected: 83.39%)
  - `[Task Completion Rate]` (Expected: 56.93%)
  - `[Containment Rate]` (Expected: 52.05%)
  - `[Resolution Rate]` (Expected: 56.17%)
  - `[Fallback Rate]` (Expected: 18.93%)
  - `[Average Confidence]` (Expected: 65.08%)
  - `[Conversation Satisfaction Proxy]` (Expected: 54.89%)

## 6. Business Impact
*Note: The semantic model currently does not contain the business impact measures, as the What-If parameters step has not been executed yet. Once they are created, use them here.*
- **Visual Type:** 4 KPI Cards
- **Fields:**
  - `[Agent Calls Avoided]` (Expected: 3,218)
  - `[Agent Hours Freed]` (Expected: 268.17 hours)
  - `[FTE Capacity Freed]` (Expected: 1.49)
  - `[Estimated Operational Cost Avoided]` (Expected: ₹160,900)

## 7. Filters (Slicers)
Place the following in a compact horizontal or slide-out filter pane:
- `dim_date[date]` (Date range)
- `dim_campaign[campaign_name]` (Campaign)
- `dim_bot[bot_name]` / `dim_bot[bot_version]` (Bot)
- `dim_customer[customer_segment]` (Customer Segment)

## 8. Design Theme Guidelines
- **Background:** White/light
- **Accents:** Dark gold / restrained gold
- **Text:** Dark neutral
- **Prohibitions:** No 3D charts, gauges, decorative donuts, unnecessary images, or gradients. Keep it professional.
