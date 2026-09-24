# Architecture Document
**Project:** Insightal AI — Conversational AI & BFSI Voice Analytics Platform

## 1. System Overview
Insightal AI uses a robust data pipeline to transform raw, synthetic conversational AI data into actionable business intelligence. The architecture scales from an initial 10K MVP to a 500K-call production load while supporting analytical queries, machine learning, and Power BI reporting.

## 2. Architecture Diagram
```text
[ Synthetic Python Generator ]
            |
            v
[ MySQL: insightal_raw ]
 (raw_customers, raw_calls, raw_conversations)
            |
            v
[ MySQL: insightal_staging ]
 (stg_customers, stg_calls, stg_conversations)
            |
            v
[ MySQL: insightal_analytics ] (Star Schema)
 (fact_calls, fact_conversation, dim_customer, dim_intent, dim_bot, dim_campaign, dim_date)
            |
   +--------+--------+
   |                 |
   v                 v
[ Python ]      [ Power BI ]
(EDA, ML)       (Dashboards)
```

## 3. Data Flow
1. **Generation:** Python script generates probabilistic synthetic data as CSV/JSON or direct SQL inserts.
2. **Raw Layer:** Data is loaded as-is into `insightal_raw`.
3. **Staging Layer:** Data is moved to `insightal_staging` where data quality checks, deduplication, and initial casting occur.
4. **Analytics Layer:** Data is transformed into a star schema in `insightal_analytics`.
5. **Consumption:** Power BI connects to the analytics layer (DirectQuery/Import). Python reads from analytics for ML/EDA.

## 4. Raw Layer (`insightal_raw`)
Stores exact replicas of generated data. No transformations. Includes intentional anomalies for data quality testing.

## 5. Staging Layer (`insightal_staging`)
Handles type casting, null handling, and deduplication. Serves as a clean source for the analytical transformation.

## 6. Analytics Layer (`insightal_analytics`)
Contains the heavily read-optimized Star Schema. All facts and dimensions reside here.

## 7. Star Schema
A standard dimensional model to support slicing and dicing metrics by customer, bot, campaign, intent, and time. Features two fact tables to manage the distinct analytical grains (call vs. turn). Time-varying attributes (like DPD) are snapshot in `fact_calls` to prevent historical overwriting.

## 8. Python Integration
- **Data Generation:** `01_data_generation.py` uses Pandas and numpy to simulate data.
- **Data Cleaning:** `02_data_cleaning.py` implements the ETL flow.
- **EDA & ML:** Separate scripts and Jupyter Notebooks run statistical analysis and train models using `scikit-learn`.

## 9. ML Architecture (Escalation Prediction)
**Target:** `escalation_flag`
**Prediction Point:** During the active call, before the final escalation outcome is known.
**Allowed Features:** Must represent information available at prediction time. Potential features:
- `intent`
- `confidence_score`
- `attempt_number`
- `call_duration_so_far`
- `sentiment_score`
- `fallback_count_so_far`
- `turn_count_so_far`
- `days_past_due_at_call`
- `dpd_bucket_at_call`
- `risk_segment_at_call`
- `customer_segment`
- `previous_call_count`
- `previous_escalation_count`
- `bot_version`
- `campaign`
- `language`

**Prohibited Features (Target Leakage Prevention):** Post-outcome fields are strictly prohibited from ML features. This includes: `escalation_flag`, `resolution_flag`, `task_completed_flag`, `containment_flag`, `ptp_flag`, `payment_status`, `payment_amount`, and any final call outcome fields.

## 10. Power BI Architecture
- **Semantic Model:** Connects strictly to `insightal_analytics`. Relationships follow the defined star schema. 
- **Relationship Guidance:** Use **single-direction relationships** wherever possible. Do NOT use unrestricted bidirectional filtering between `fact_calls` and `fact_conversation`.
- **Role-Playing Dimensions:** `dim_intent` has two logical roles in `fact_conversation` (`expected_intent_key` and `detected_intent_key`). This will be modeled using an active relationship for the primary role and an inactive relationship (with DAX `USERELATIONSHIP` activation) for the secondary role to avoid ambiguous filter paths.
- **Pages Supported:** Executive Overview, Call Operations, AI Performance, Customer Journey, BFSI Collections, Business Impact.
- **What-If Analysis:** Configurable parameters for agent cost and containment improvements will be built as independent disconnected tables/parameters in Power BI.

## 11. Scalability Considerations
- **Indexing:** B-Tree indexes on primary keys, foreign keys, and specific composite combinations like `(date_key, escalation_flag)` and `(bot_key, date_key)`. Avoid excessive single-column boolean indexing.
- **Volume:** At 500K calls and ~3M conversation turns, standard MySQL is sufficient, but indexing is critical. 

## 12. Privacy Considerations
All data is strictly synthetic. Identifiers are UUIDs or synthetic integers. India-focused geography uses categorical state/city names without addresses.

## 13. Design Decisions
- **Separate Schemas vs Table Prefixes:** **Decision:** Separate schemas (`insightal_raw`, `insightal_staging`, `insightal_analytics`). **Why:** It enforces strict separation of concerns, simplifies user permissions in a real-world scenario, and keeps the analytics schema perfectly clean for BI tools without cluttering it with staging tables.
- **Two Fact Tables:** **Decision:** `fact_calls` and `fact_conversation`. **Why:** To prevent massive data duplication (e.g., call duration repeating for every turn) and to ensure accurate denominator counts for call-level vs turn-level metrics.

## 14. Trade-offs
- Storing synthetic ground-truth intents alongside detected intents slightly inflates the `fact_conversation` table width, but is strictly necessary to calculate True Intent Recognition Accuracy.
- Separating raw/staging/analytics requires more storage, but preserves the data engineering lineage.

## 15. Future Extension Points
- Can add a `fact_financial_transactions` table if the BFSI scope expands beyond collections.
- Can partition tables by month for massive scale.
