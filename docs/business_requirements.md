# Business Requirements Document (BRD)
**Project:** Insightal AI — Conversational AI & BFSI Voice Analytics Platform

## 1. Project Context
Insightal AI is a fictional BFSI (Banking, Financial Services, and Insurance) technology company that provides AI-powered voice agents for financial-services organizations. The platform handles customer conversations for use cases such as loan collections, payment reminders, loan applications, loan status, EMI queries, loan eligibility, insurance renewals, insurance claims, premium queries, customer support, payment failures, customer complaints, and lead qualification. 

The project is NOT intended to build the voice AI itself. Instead, it analyzes the output and performance of the voice AI. The analytics platform should answer: *How well is the AI voice agent performing, where are customers dropping off, when does AI require human intervention, and what business value is generated through automation?*

## 2. Business Problem
Financial institutions process large volumes of customer conversations. Traditional call-center operations can be expensive and difficult to scale. AI voice agents can automate routine conversations, but organizations need visibility into call performance, connectivity, customer engagement, intent recognition, confidence, fallbacks, escalation, task completion, resolution, customer journey drop-offs, collections outcomes, and business impact. The analytics platform should provide a unified view of these areas.

## 3. Business Objectives
### Objective 1 — Operational Visibility
Measure call volume, connection rate, call duration, attempts, hang-up reasons, and calling patterns.

### Objective 2 — AI Performance Evaluation
Measure intent recognition, confidence, fallback, containment, escalation, task completion, resolution, and bot-version performance.

### Objective 3 — Customer Journey Optimization
Identify funnel drop-offs, conversation bottlenecks, failed tasks, escalation points, and repeat calls.

### Objective 4 — BFSI Collections Analytics
Measure reachability, Promise to Pay (PTP), successful PTP, collection conversion, collection amount, and DPD/risk-segment performance.

### Objective 5 — Business Impact
Estimate operational cost avoided, additional calls automated, operational capacity freed, and potential collection value.

### Objective 6 — Predictive Analytics
Identify factors associated with human escalation, failed task completion, and poor conversation outcomes.

## 4. Stakeholders
- **COO / Executive Sponsor:** Interested in overall performance, operational efficiency, AI automation, and estimated cost impact.
- **Head of Collections:** Interested in contactability, PTP, successful payments, collections, DPD segments, and campaign performance.
- **Conversational AI Product Manager:** Interested in intent performance, confidence, fallback, escalation, containment, and bot-version performance.
- **Operations Manager:** Interested in call volume, connectivity, duration, attempts, hang-up reasons, and campaign performance.
- **Data Analyst:** Interested in KPIs, trends, segmentation, root-cause analysis, and business insights.
- **Data Engineer:** Interested in data quality, ETL, data consistency, and pipeline reliability.
- **ML Engineer:** Interested in features, escalation prediction, model performance, and explainability.
- **Collections Agent:** Interested in high-risk customers, failed conversations, and follow-up opportunities.

## 5. User Personas
1. **Executive Sponsor:** Role: C-level executive. Goal: Understand platform ROI and cost savings. Questions: How much are we saving? Dashboard: Executive Overview. Decisions: Budget allocation for AI projects.
2. **Operations Manager:** Role: Call center operations leader. Goal: Maximize contactability. Questions: When are the best times to call? Dashboard: Call Operations. Decisions: Campaign scheduling and retries.
3. **Product Manager (Conversational AI):** Role: Bot performance owner. Goal: Improve bot accuracy and containment. Questions: Which intents fail most often? Dashboard: AI Performance. Decisions: Which intents need retraining.
4. **Data Analyst:** Role: Insights generator. Goal: Deliver actionable insights to business users. Questions: What drives repeat calls? Dashboard: All dashboards. Decisions: Identifying deep-dive analysis areas.
5. **ML Engineer:** Role: Predictive modeler. Goal: Deploy escalation prediction model. Questions: What features predict escalation? Dashboard: Predictive Analytics. Decisions: Model feature selection and tuning.
6. **Collections Manager/Agent:** Role: Debt recovery specialist. Goal: Maximize collections. Questions: Which DPD buckets have low PTP? Dashboard: BFSI Collections. Decisions: Target highest risk profiles manually.

## 6. Business Questions
### Operational Analytics
- How many calls are being made?
- How many are connected?
- What is the connection rate?
- When are peak calling periods?
- What is average call duration?
- How many attempts are required?
- What are the major hang-up reasons?

### AI Analytics
- How accurately is the AI recognizing intents?
- Which intents have the lowest confidence?
- Which intents have the highest fallback?
- Which intents have the highest escalation?
- What is the containment rate?
- Which bot version performs better across key metrics? *(Note: Do not rank or label bot versions as "best". Present factual metric differences).*

### Customer Journey
- Where do customers drop out?
- Which journey stages have the highest drop-off?
- Which intents have poor task completion?
- Which customer segments show high repeat-call behavior?

### Collections
- What is the contact rate?
- What is the PTP rate?
- Which DPD buckets have lower PTP?
- Which customer segments have higher successful payment rates?
- Which campaigns generate stronger collection outcomes?

### Business Impact
- How many calls were successfully automated?
- What is the estimated operational cost avoided?
- How does improved containment affect operational capacity?
- What is the estimated collection value?

### Predictive Analytics
- Which features are associated with human escalation?
- Can escalation risk be predicted before the call outcome is known?
- How well does the model identify high-risk conversations?

## 7. Functional Requirements
- **FR-01 — Synthetic Data Generation:** Generate realistic synthetic customers, calls, conversations, campaigns, bots, intents, and collections outcomes.
- **FR-02 — Data Storage:** Support raw, staging, and analytical data layers (MySQL).
- **FR-03 — Data Quality:** Detect missing values, duplicates, invalid records, invalid timestamps, and invalid relationships.
- **FR-04 — SQL Analytics:** Provide analytical queries/views for all major KPIs.
- **FR-05 — Python Analytics:** Support EDA, statistical analysis, customer segmentation, AI-performance analysis, and business-impact calculations.
- **FR-06 — Predictive Analytics:** Predict the probability of human escalation.
- **FR-07 — Power BI:** Provide six dashboard pages (Executive Overview, Call Operations, AI Performance, Customer Journey, BFSI Collections, Business Impact).
- **FR-08 — What-If Analysis:** Allow configurable assumptions for Human-agent cost, Containment improvement, and Collection improvement.

## 8. Non-Functional Requirements
- **Scalability:** Initial MVP: 10K calls. Final scale: 100K–500K calls.
- **Performance:** SQL and Power BI models should remain performant at the target scale.
- **Reproducibility:** All synthetic data generation and analytical transformations must be reproducible.
- **Explainability:** ML models must have interpretable features and business explanations.
- **Maintainability:** Scripts and documentation should be organized logically.
- **Data Privacy:** The project must use synthetic data only. Never use real customer information, phone numbers, names, addresses, Aadhaar, PAN, bank accounts, real call recordings, or confidential company data.

## 9. KPI Framework
### Operational KPIs
- **Total Calls:** Number of call records initiated. (Grain: Call)
- **Connected Calls:** Calls successfully connected to a customer. (Grain: Call)
- **Connection Rate:** `(Connected Calls / Total Calls) × 100`
- **Average Call Duration:** Average duration of connected calls.
- **Median Call Duration:** Median duration of connected calls.
- **Average Attempts:** Average number of attempts per customer.

### AI Performance KPIs
- **Intent Recognition Accuracy:** Measures whether the detected intent matches the ground-truth intent. `(Accurately Detected Intents / Total Intents) × 100`. (Grain: Conversation Turn)
- **Average Confidence Score:** Average model confidence for eligible conversation turns.
- **Fallback Rate:** `(Fallback Turns / Total Eligible Conversation Turns) × 100`
- **Containment Rate:** `(Successfully AI-contained Calls / Eligible Connected Calls) × 100` (Eligibility: calls meant for AI containment, excluding immediate hangups).
- **Escalation Rate:** `(Human Escalation Calls / Eligible Connected Calls) × 100`
- **Task Completion Rate:** `(Completed Tasks / Started Tasks) × 100`
- **Resolution Rate:** `(Successfully Resolved Calls / Eligible Connected Calls) × 100`

### BFSI Collections KPIs
- **Contact Rate:** `(Customers Contacted / Total Unique Customers Targeted) × 100`
- **PTP Rate:** `(Calls Resulting in PTP / Eligible Connected Collections Calls) × 100`
- **Successful PTP Rate:** `(PTPs Resulting in Actual Payment / Total PTPs) × 100`
- **Collection Conversion Rate:** `(Customers Making a Successful Payment / Customers with a PTP) × 100`
- **PTP Amount:** Total promised payment amount.
- **Successful Collection Amount:** Total actual payment amount.
- **Outstanding Amount:** Total outstanding amount associated with the eligible population.

### Business Impact KPIs
- **Estimated Operational Cost Avoided:** `AI-contained calls × Assumed human-agent cost per call`. (This is an estimate).
- **Additional Calls Automated:** Based on an assumed improvement in containment.
- **Operational Capacity Freed:** Calculated based on average call duration saved vs agent capacity.

## 10. Satisfaction Proxy
- **Conversation Satisfaction Proxy:** A project-defined analytical proxy. It uses metrics like sentiment, resolution, escalation, task completion, and repeat-call behavior to estimate satisfaction. *This is NOT actual CSAT, but a proxy metric designed for this portfolio project.*

## 11. Bot Quality Score
- **Formula:** `(30% × Containment Rate) + (25% × Task Completion Rate) + (20% × Intent Recognition) + (15% × Satisfaction Proxy) + (10% × Reliability)`. 
- **Notes:** This is a custom analytical metric created for this portfolio project. It is NOT an industry-standard metric. Use it as an analytical framework to compare bot versions, not to declare one version universally "best".

## 12. Predictive Analytics Requirements
- **Target:** `escalation_flag`
- **Potential Features:** Intent, Confidence, Call duration, Attempt number, Sentiment, Customer segment, DPD, Previous calls, Previous fallback count, Bot version, Campaign, Language.
- **Evaluation:** Precision, Recall, F1, ROC-AUC, Confusion Matrix. Evaluate based on predictive signal, generalization, feature interpretability, and business usefulness. The prediction point is during the call before the outcome is known.

## 13. Bot Version Analysis
- **Versions:** Compare versions like Insightal Voice v1.0, v1.1, v2.0, v2.1.
- **Analysis:** Compare factual differences in intent recognition, confidence, fallback, containment, escalation, task completion, and resolution. Do not introduce a subjective overall ranking.

## 14. Customer Geography
Use **India-focused synthetic geography**. 
- **Preferred States:** Maharashtra, Karnataka, Telangana, Andhra Pradesh, Tamil Nadu, Delhi, Haryana, Gujarat, Uttar Pradesh, West Bengal, Kerala, Rajasthan, Madhya Pradesh, Punjab.
- **Example Cities:** Mumbai, Pune, Bengaluru, Hyderabad, Chennai, Delhi, Gurugram, Noida, Ahmedabad, Kolkata, Jaipur, Lucknow, Kochi, Vijayawada, Visakhapatnam.
- **Constraints:** Do NOT generate real residential addresses. City/state should be categorical synthetic attributes only.

## 15. Data Grain Requirements
1. **Call Level:** One row = one call. Used for Connection, Duration, Containment, Escalation, Task completion, Resolution, PTP, Payment.
2. **Conversation Turn Level:** One row = one utterance/turn. Used for Intent recognition, Confidence, Fallback, Sentiment.

## 16. Project Scope
- Synthetic data generation
- Data quality
- SQL analytics
- Python analytics
- Customer segmentation
- Escalation prediction
- Business impact analysis
- Power BI dashboards
- Documentation
- GitHub packaging

## 17. Out of Scope
- Real-time Kafka/Spark architecture
- Real telephony integrations (Twilio/Avaya)
- Actual dialer integration
- Building the voice AI model
- Building an NLP model from scratch
- Real customer data or production deployment
- Actual financial transactions or real-time banking integrations

## 18. Assumptions
- Insightal AI is a fictional company and all data is synthetic.
- Voice agents produce transcriptions, intents, confidence scores, and sentiment per turn.
- The platform primarily supports outbound BFSI campaigns with some inbound support.
- Human-agent cost is an assumption; business-impact calculations are estimates.
- Synthetic relationships are designed to resemble plausible real-world patterns but are not claims about actual industry performance.

## 19. Risks and Mitigations
- **Synthetic Data Risk:** Data may oversimplify real-world behavior. *Mitigation:* Use probabilistic relationships, random noise, multiple segments, and controlled anomalies.
- **ML Risk:** Synthetic relationships may make prediction unrealistically easy. *Mitigation:* Feature overlap, train/test separation, cross-validation, and leakage checks.
- **KPI Risk:** Incorrect denominators may produce misleading results. *Mitigation:* Explicit KPI definitions, documented grain, and validation tests.
- **BI Risk:** Large datasets may affect Power BI performance. *Mitigation:* Use star schema, proper relationships, and aggregations.

## 20. Success Criteria
Phase 1 is complete as the BRD successfully covers: Business problem, objectives, stakeholders, personas, business questions, functional/non-functional requirements, strict KPI definitions with formulas/grains, intent recognition methodologies, Satisfaction Proxy, Bot Quality Score, predictive requirements, version analysis, India-focused synthetic geography, explicit scope inclusions/exclusions, and documented assumptions/risks without contradictions or real PII required.
