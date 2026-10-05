# Phase 13 Artifact Inventory

## 1. Power BI Artifacts

| Path | Type | Final Candidate? | Notes |
|---|---|---|---|
| `C:\Users\TVL SWAMY\Desktop\DA_1\Insightal_AI_BFSI_Analytics.pbip` | PBIP Root | No | Saved on Desktop outside repo. Intermediate version. |
| `C:\Users\TVL SWAMY\Desktop\DA_1\Insightal_AI_BFSI_Analytics.Report` | PBIR Report | No | Contains 5 pages including stale "Scenario Analysis" and "Customer Insights", failing the final 4-page requirement. |
| `C:\Users\TVL SWAMY\Desktop\DA_1\Insightal_AI_BFSI_Analytics.SemanticModel` | PBIR Model | No | Contains Phase 9 tables and role-playing dimensions, but paired with the incomplete report. |

## 2. PBIX Candidates

| Path | Size | Final Candidate? | Notes |
|---|---:|---|---|
| `C:\Users\TVL SWAMY\Desktop\DA_1\Insightal_AI_BFSI_Analytics.pbix` | 441 KB | No | Found on Desktop outside repo. Intermediate draft accompanying the PBIP. |

## 3. PBIP/PBIR Candidates

| Path | Type | Final Candidate? | Notes |
|---|---|---|---|
| (See Section 1 above) | | | No finalized 4-page PBIP/PBIR exists in the accessible workspace. |

## 4. pbix_unzipped Assessment

- **Path:** `C:\Users\TVL SWAMY\Desktop\DA_1\conversational-ai-bfsi-analytics\pbix_unzipped`
- **Contents:** Extracted PBIX components (`DataModel` at 3.4MB, `Report/Layout`).
- **Status:** The `Layout` file specifies exactly 1 page (`Page 1`), completely failing the Phase 9 requirement.
- **Classification:** It is an abandoned/intermediate extraction, not a valid PBIP, and contains no useful final artifacts. It is safe to delete.

## 5. Root Temporary Files

| File / Folder | Classification | Reason |
|---|---|---|
| `call_mcp*.py` (20+ files) | DELETE | Scratchpad scripts used to iteratively call MCP tools. |
| `pbi_*.py` (8+ files) | DELETE | One-off Power BI manipulation and creation scripts. |
| `test_dax*.py`, `run_dax.py` | DELETE | Temporary DAX validation scripts. |
| `inspect_*.ps1`, `inspect_*.py` | DELETE | Ad-hoc debugging scripts. |
| `get_*.py`, `list_*.py`, `mark_*.py` | DELETE | Helper scripts used during development. |
| `apply_redesign*.py`, `*whatif.py` | DELETE | Feature-specific development scripts. |
| `inventory.py`, `parse_report.py`, etc | DELETE | Transient parsing utilities. |
| `measures.txt`, `rels.txt`, `inventory_output.txt` | DELETE | Plain-text outputs from previous debug runs. |
| `artifacts/ml/` | KEEP | Required project outputs containing the final champion models and explainability figures. |

## 6. Archives / Large Files

| File | Classification | Reason |
|---|---|---|
| `model.zip` (3.4 MB) | DELETE | Extracted/temporary archive of a Semantic Model. |
| `model_new.zip` (3.4 MB) | DELETE | Extracted/temporary archive of a Semantic Model. |
| `pbix_unzipped/` (3.4 MB) | DELETE | Exploded intermediate PBIX without final report pages. |

## 7. .env Security Status

- **Exists:** Yes, located at repository root.
- **Git Status:** Properly ignored (present in `.gitignore`) and currently untracked.
- **Contents:** Contains local database connection defaults (`root` user, empty password).
- **Security Assessment:** No sensitive production secrets are exposed.
- **Recommendation:** Safe to delete to keep the repository perfectly clean, as instructions for local DB connections should ideally reside in the `README.md`.

## 8. Git Status

- **Branch:** `main`
- **Remote:** Unknown/None tracked.
- **Tracked State:** Clean. All modifications to documentation and ML scripts from Phase 12 have been successfully committed previously, or there are no uncommitted tracked changes.
- **Untracked State:** Extremely cluttered. Contains over 60 temporary scripts, text files, and directories (as detailed in Sections 4, 5, and 6).

## 9. Recommended Safe Actions

**MUST KEEP:**
- `artifacts/ml/` (Do not delete or modify this folder; it contains the frozen Phase 10-12 ML deliverables).

**SAFE TO MOVE:**
- None. The temporary scripts are highly context-specific and redundant.

**SAFE TO DELETE:**
- `pbix_unzipped/` directory
- `model.zip`, `model_new.zip`
- All `call_mcp*.py`, `pbi_*.py`, `test_dax*.py`, `inspect_*.py`, `inspect_*.ps1`, `apply_redesign*.py`, `*whatif*.py`, `get_*.py`, `list_*.py`, `mark_*.py` scripts.
- `inventory.py`, `parse_report.py`, `run_dax.py`, `scan_datamodel.py`, `test_pass.py`, `validate_page1.py`, `update_collections_measures.py`
- `measures.txt`, `rels.txt`, `inventory_output.txt`
- `.env`

**REQUIRES USER DECISION:**
- How to handle the missing Power BI `.pbip`. Since the Desktop project was completed manually but not committed, the user must decide whether to extract the final `.pbip` from their manual Desktop file and add it to the repo, or proceed to final packaging with only the SQL/Python/ML artifacts.
