import pandas as pd
from src.data_generator.random_state import get_rng

def generate_intents():
    intents = [
        # Collections
        {'intent_id': 'INT_PAY_REMIND', 'intent_name': 'Payment Reminder', 'intent_category': 'Collections', 'business_function': 'Debt Recovery', 'expected_task': 'Remind Payment'},
        {'intent_id': 'INT_PTP', 'intent_name': 'Promise to Pay', 'intent_category': 'Collections', 'business_function': 'Debt Recovery', 'expected_task': 'Capture Date'},
        {'intent_id': 'INT_PAY_DIFF', 'intent_name': 'Payment Difficulty', 'intent_category': 'Collections', 'business_function': 'Debt Recovery', 'expected_task': 'Offer Restructure'},
        {'intent_id': 'INT_OVERDUE', 'intent_name': 'Overdue Payment', 'intent_category': 'Collections', 'business_function': 'Debt Recovery', 'expected_task': 'Collect Payment'},
        {'intent_id': 'INT_PAY_CONF', 'intent_name': 'Payment Confirmation', 'intent_category': 'Collections', 'business_function': 'Debt Recovery', 'expected_task': 'Confirm Payment'},
        # Loan
        {'intent_id': 'INT_LOAN_APP', 'intent_name': 'Loan Application', 'intent_category': 'Loan', 'business_function': 'Retail Banking', 'expected_task': 'Start Application'},
        {'intent_id': 'INT_LOAN_STAT', 'intent_name': 'Loan Status', 'intent_category': 'Loan', 'business_function': 'Retail Banking', 'expected_task': 'Provide Status'},
        {'intent_id': 'INT_LOAN_ELIG', 'intent_name': 'Loan Eligibility', 'intent_category': 'Loan', 'business_function': 'Retail Banking', 'expected_task': 'Check Eligibility'},
        {'intent_id': 'INT_EMI_QUERY', 'intent_name': 'EMI Query', 'intent_category': 'Loan', 'business_function': 'Retail Banking', 'expected_task': 'Provide EMI Details'},
        {'intent_id': 'INT_OUTSTAND_AMT', 'intent_name': 'Outstanding Amount', 'intent_category': 'Loan', 'business_function': 'Retail Banking', 'expected_task': 'Provide Balance'},
        # Insurance
        {'intent_id': 'INT_PREM_QUERY', 'intent_name': 'Premium Query', 'intent_category': 'Insurance', 'business_function': 'Insurance', 'expected_task': 'Provide Premium'},
        {'intent_id': 'INT_RENEWAL', 'intent_name': 'Policy Renewal', 'intent_category': 'Insurance', 'business_function': 'Insurance', 'expected_task': 'Renew Policy'},
        {'intent_id': 'INT_CLAIM_STAT', 'intent_name': 'Claim Status', 'intent_category': 'Insurance', 'business_function': 'Insurance', 'expected_task': 'Provide Status'},
        {'intent_id': 'INT_CLAIM_QUERY', 'intent_name': 'Claim Query', 'intent_category': 'Insurance', 'business_function': 'Insurance', 'expected_task': 'Explain Claim'},
        # Support
        {'intent_id': 'INT_PAY_FAIL', 'intent_name': 'Payment Failure', 'intent_category': 'Support', 'business_function': 'Customer Service', 'expected_task': 'Resolve Failure'},
        {'intent_id': 'INT_ACCT_QUERY', 'intent_name': 'Account Query', 'intent_category': 'Support', 'business_function': 'Customer Service', 'expected_task': 'Provide Info'},
        {'intent_id': 'INT_COMPLAINT', 'intent_name': 'Complaint', 'intent_category': 'Support', 'business_function': 'Customer Service', 'expected_task': 'Log Complaint'},
        {'intent_id': 'INT_GEN_SUPPORT', 'intent_name': 'General Support', 'intent_category': 'Support', 'business_function': 'Customer Service', 'expected_task': 'Provide Support'},
        # Lead Qualification
        {'intent_id': 'INT_PROD_INT', 'intent_name': 'Product Interest', 'intent_category': 'Lead Qualification', 'business_function': 'Sales', 'expected_task': 'Qualify Lead'}
    ]
    
    df = pd.DataFrame(intents)
    df.insert(0, 'intent_key', range(1, len(df) + 1))
    
    difficulty_map = {
        'INT_PAY_REMIND': 0.1, 'INT_PTP': 0.4, 'INT_PAY_DIFF': 0.7, 'INT_OVERDUE': 0.5, 'INT_PAY_CONF': 0.0,
        'INT_LOAN_APP': 0.6, 'INT_LOAN_STAT': 0.1, 'INT_LOAN_ELIG': 0.3, 'INT_EMI_QUERY': 0.2, 'INT_OUTSTAND_AMT': 0.1,
        'INT_PREM_QUERY': 0.1, 'INT_RENEWAL': 0.3, 'INT_CLAIM_STAT': 0.2, 'INT_CLAIM_QUERY': 0.5,
        'INT_PAY_FAIL': 0.6, 'INT_ACCT_QUERY': 0.2, 'INT_COMPLAINT': 0.8, 'INT_GEN_SUPPORT': 0.4,
        'INT_PROD_INT': 0.2
    }
    
    df['base_difficulty'] = df['intent_id'].map(difficulty_map)
    return df
