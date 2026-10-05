# ML Escalation Prediction Specification

## 1. Business Problem
The objective is to predict whether a Conversational AI interaction will eventually escalate to a human agent, based solely on information available early in the interaction. This enables early intervention, agent handoff prioritization, operational monitoring, and proactive routing. The model simulates a real-time prediction scenario during an active call.

## 2. Target
The target variable is a derived training target: `escalation_after_t3` (Binary: 0 or 1).
- **1:** An escalation event occurs strictly after the timestamp of the 3rd customer turn.
- **0:** The call reaches its end without a future escalation after the 3rd customer turn.
*Note:* The final call-level `escalation_flag` may be used as an outcome source during label construction, but must NOT be treated as automatically equivalent to `escalation_after_t3`.

## 3. Prediction Point & Unit
- **Prediction Point:** Immediately after the **3rd customer turn** within a conversation.
- **Temporal Definition:** 
  - `prediction_timestamp` = timestamp of the 3rd customer turn.
  - Future escalation means: `escalation_event_timestamp > prediction_timestamp` (strict greater-than logic).
- **Eligibility:** For this fixed-point model, we only include calls that represent a genuine opportunity to predict *future* escalation.
  - **Include:** Calls with at least 3 customer turns, valid Turn-3 timestamp, valid call start timestamp, and valid required identifiers.
  - **Exclude:** Calls terminating before the 3rd customer turn, and calls where an escalation event already occurred at or before the Turn-3 prediction timestamp.
- **Prediction Unit:** A point-in-time snapshot of the eligible call and customer state up to and including the `prediction_timestamp`.

## 4. Feature Groups
Features are divided into four primary groups:
1. **Conversation Context:** Dynamic state of the current call as of the 3rd customer turn (e.g., rolling fallback counts, cumulative duration, running confidence average, sentiment).
2. **Call Metadata:** Attributes established at call initiation (e.g., campaign, bot version, language).
3. **Customer Historical Profile:** Behavioral indicators derived *only* from calls terminating before the current call's start time (e.g., prior escalations, prior call counts).
4. **Collections Context:** Point-in-time snapshots of debt and risk (e.g., DPD, outstanding amount, risk segment).

## 5. Feature Availability Timing
To enforce a strict real-time prediction simulation, features are classified by availability:
- **Historical Pre-Call:** Data known before the current call starts.
- **Point-In-Time (Turn 3):** Metrics accumulated exactly up to the end of the 3rd customer utterance. Any events occurring on Turn 4 or later are strictly hidden.

## 6. Leakage Rules
Leakage prevention is the highest technical priority. The following strict rules apply:
- The target `escalation_flag` and deterministic indicators (`escalation_trigger_flag`) are prohibited from the model feature matrix. `escalation_trigger_flag` may be used ONLY during target/label construction to determine whether a future escalation occurred.
- Ground truth variables (`expected_intent_key`) are prohibited.
- Final call outcomes (`resolution_flag`, `containment_flag`, `task_completed_flag`, `ptp_flag`, `payment_status`, `payment_amount`, `call_status`, `hangup_reason`) are prohibited.
- Final call aggregates (e.g., total `call_duration_seconds`, final overall `confidence_score`) are prohibited. They must be replaced with running aggregates (e.g., `call_duration_so_far`, `running_confidence_score_at_turn_3`).
- Customer historical aggregates must explicitly filter out the current call and any future calls based on exact chronological timestamps.

## 7. Train/Validation/Test Strategy
Due to the temporal nature of customer behavior and potential model drift over time, a **Time-Based Split** will be utilized rather than a random split.
- **Train:** Earliest chronologically sorted interactions (e.g., first 70% of calls).
- **Validation:** Subsequent 15% of interactions, used for hyperparameter tuning.
- **Test:** Final 15% of interactions, representing a "future" production deployment scenario.

*Customer Overlap Analysis:* An explicit customer-overlap analysis must be conducted and documented to measure how many customers in the Validation/Test sets also appeared in the Train set. If severe overlap exists, we must evaluate whether it creates an unrealistic evaluation scenario and document the decision.

*Note: Strict chronological splitting prevents future information from bleeding into the training phase and ensures an honest evaluation of generalizability.*

## 8. Evaluation Metrics
Since the escalation rate is approximately 36.23%, accuracy alone is insufficient. The model will be evaluated on:
- **ROC-AUC:** Overall ability to rank risk.
- **PR-AUC:** Performance on the positive (escalation) class.
- **Recall (Sensitivity):** Priority metric for business, as missing a high-risk escalation is costly.
- **Precision:** Monitored to avoid flooding agents with false positives.
- **F1-Score:** Harmonic mean of precision and recall.
- **Calibration Curve:** To ensure predicted probabilities align with actual escalation rates.

## 9. Baseline Model
- **Algorithm:** Logistic Regression.
- **Preprocessing:** Standard scaling for continuous features, One-Hot Encoding for categoricals, and simple imputation if necessary.
- **Rationale:** Highly interpretable, fast to train, and sets a strong mathematical baseline for linear relationships.

## 10. Candidate Models
- **Random Forest:** To capture non-linear interactions without severe overfitting.
- **XGBoost:** Gradient boosted trees, generally providing state-of-the-art performance on tabular data and handling missing values natively.
*Complexity will be strictly limited to these standard algorithms to prioritize reproducibility over framework complexity.*

## 11. Explainability Approach
Explainability is mandatory for portfolio-grade analytics.
- **Logistic Regression:** Feature importance will be derived directly from normalized coefficients.
- **Tree-Based Models:** Permutation importance and SHAP (SHapley Additive exPlanations) summary plots will be used to show both the magnitude and direction of feature impacts on model predictions.

## 12. Business Interpretation
The output of the model will be framed as risk associations, not causal claims. For example:
> "Feature importance indicates that low running confidence by Turn 3 is strongly associated with a higher model prediction for escalation risk."

## 13. Deployment Concept
While physical deployment is out of scope for this phase, the conceptual architecture is a real-time microservice that receives a payload of the conversation state at Turn 3, evaluates the XGBoost/Logistic artifact, and returns an `escalation_probability` score back to the Conversational AI routing engine.

## 14. Monitoring Concept
In production, the model would require monitoring for:
- **Data Drift:** Changes in the distribution of input features (e.g., sudden spikes in unknown intents).
- **Concept Drift:** Changes in the relationship between features and escalation (e.g., users escalating less frequently despite fallbacks due to a new bot persona).
- **Performance:** Tracking real-world Precision and Recall based on actual finalized call outcomes.

## 15. Limitations
- The model evaluates only calls that survive to a 3rd customer turn. Immediate escalations or drops on Turn 1 or 2 require separate heuristic rules.
- Sentiment extraction relies on the upstream NLP system; inaccuracies in real-time sentiment will propagate to the prediction.

## 16. Synthetic-Data Disclosure
This model is trained on a rigorously generated synthetic dataset containing intentional data-generation rules (e.g., lower confidence leading to higher fallback incidence). The learned feature importances reflect these synthetic generation rules. Therefore, biological or sociological causal claims should not be extrapolated from these results to real-world populations.
