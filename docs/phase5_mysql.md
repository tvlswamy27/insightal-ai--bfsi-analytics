# Phase 5: MySQL Database Implementation

This document describes the design and implementation of the Insightal AI MySQL database (Phase 5).

## 1. Objective
Implement a multi-tier data warehouse architecture within MySQL 8.x, demonstrating:
* Raw Data Ingestion (schema-on-read style loading).
* Staging & Data Quality Transformations (handling missing values, data type normalization, error flagging).
* Dimensional Modeling (Star Schema) matching the approved Phase 3 data dictionary.
* Reproducibility (via an orchestrated Python/SQL ETL pipeline).

## 2. Architecture

The pipeline consists of three logical databases/schemas:

### 2.1 `insightal_raw`
- **Purpose**: Lands the Phase 4 synthetic CSV files as-is.
- **Tables**: `raw_customers`, `raw_calls`, `raw_conversations`.
- **Characteristics**: All columns are stored as `TEXT`. No constraints or primary keys. It serves strictly as a landing zone.
- **Loading Mechanism**: Handled via Python `pandas.to_sql` batched inserts since the environment's `local_infile` is `OFF`.

### 2.2 `insightal_staging`
- **Purpose**: Cleanses data and enforces basic types, but maintains the flat structure of the raw layer. Identifies and flags anomalies injected during Phase 4 without dropping rows.
- **Tables**: `stg_customers`, `stg_calls`, `stg_conversations`.
- **Characteristics**:
    - Data types are cast (e.g., `VARCHAR`, `INT`, `DATETIME`, `DECIMAL`).
    - Two additional columns: `error_flag` (TINYINT) and `error_reason` (TEXT).
    - Deduplication: Handled via `SELECT DISTINCT` during ingestion from `insightal_raw` to remove pure duplicates.

### 2.3 `insightal_analytics`
- **Purpose**: The final Star Schema optimized for BI (Power BI) and ML feature extraction. 
- **Characteristics**: 
    - Strict referential integrity (Foreign Keys).
    - Surrogate keys (INT UNSIGNED).
    - Optimized indexes for analytical queries.

#### Dimensions
1. **`dim_customer`**: SCD Type 1 attributes for the synthetic customers.
2. **`dim_campaign`**: Marketing and collections campaigns.
3. **`dim_bot`**: Bot version and configuration metadata.
4. **`dim_intent`**: The fixed 19 business intents.
5. **`dim_date`**: Calendar dimension covering Jan 2025 – Dec 2027, including Indian Financial Year calculations.

#### Facts
1. **`fact_calls`**: (32 columns) Grain = One call. Contains snapshot characteristics (e.g. `outstanding_amount_at_call`) and call-level outcomes (`containment_flag`, `escalation_flag`, `payment_amount`).
2. **`fact_conversation`**: (15 columns) Grain = One utterance/turn. Links expected vs detected intents, confidence scores, and fallback indicators per turn.

## 3. Execution (Rebuilding the Database)

A Python orchestration script (`run_etl.py`) sequentially executes the SQL pipeline:

1. `sql/01_create_databases.sql`
2. `sql/02_create_raw_tables.sql`
3. `sql/04_create_staging_tables.sql`
4. `sql/05_transform_to_staging.sql`
5. `sql/06_create_dimensions.sql`
6. `sql/07_populate_dimensions.sql`
7. `sql/08_create_facts.sql`
8. `sql/09_populate_facts.sql`
9. `sql/10_create_indexes.sql`

To run manually:
```bash
python run_etl.py
```
*(Requires a `.env` file containing `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`)*

## 4. Validation
Post-execution, the pipeline runs `sql/11_validate_database.sql` to verify:
- Row counts across all layers.
- Zero foreign key violations (no orphan records).
- Strict payment and attribution rules (e.g., `payment_status = 'Success'` implies `payment_amount > 0`).

The validation results are automatically captured and exported to `docs/phase5_validation_report.md`.
