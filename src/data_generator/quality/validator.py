import pandas as pd
import json

def run_validation():
    print("Running Validation...")
    calls = pd.read_csv('data/clean/calls.csv')
    cust = pd.read_csv('data/clean/customers.csv')
    conv = pd.read_csv('data/clean/conversations.csv')
    
    report = {
        'row_counts': {
            'customers': len(cust),
            'calls': len(calls),
            'conversations': len(conv)
        },
        'business_rules_violations': 0,
        'leakage_violations': 0
    }
    
    violations = calls[(calls['escalation_flag'] == 1) & (calls['containment_flag'] == 1)]
    if not violations.empty:
        report['business_rules_violations'] += len(violations)
        print("VIOLATION: Escalation and Containment both 1")
        
    pay_violations = calls[(calls['payment_status'] == 'Success') & (calls['ptp_flag'] == 0)]
    if not pay_violations.empty:
        report['business_rules_violations'] += len(pay_violations)
        print("VIOLATION: Payment Success without PTP")
        
        
    # Check zero payment amount
    zero_pay = calls[(calls['payment_status'] == 'Success') & ((calls['payment_amount'] <= 0) | calls['payment_amount'].isna())]
    if not zero_pay.empty:
        report['business_rules_violations'] += len(zero_pay)
        print("VIOLATION: Payment Success with zero or null amount")
        
    # Check column counts
    if len(calls.columns) != 32:
        report['business_rules_violations'] += 1
        print(f"VIOLATION: calls.csv has {len(calls.columns)} columns instead of 32")
    if len(conv.columns) != 15:
        report['business_rules_violations'] += 1
        print(f"VIOLATION: conversations.csv has {len(conv.columns)} columns instead of 15")
    if len(cust.columns) != 12:
        report['business_rules_violations'] += 1
        print(f"VIOLATION: customers.csv has {len(cust.columns)} columns instead of 12")
        
    with open('data/validation/data_quality_report.json', 'w') as f:
        json.dump(report, f, indent=2)
        
    print("Validation complete. Generating Stats.")
    generate_stats(calls, conv)

def generate_stats(calls, conv):
    stats = {}
    stats['total_calls'] = len(calls)
    stats['connected_calls'] = int((calls['connection_status'] == 'Connected').sum())
    stats['connection_rate'] = stats['connected_calls'] / len(calls) if len(calls) > 0 else 0
    stats['average_duration'] = float(calls[calls['connection_status'] == 'Connected']['call_duration_seconds'].mean())
    
    stats['containment_rate'] = float(calls['containment_flag'].sum() / stats['connected_calls']) if stats['connected_calls'] > 0 else 0
    stats['resolution_rate'] = float(calls['resolution_flag'].sum() / stats['connected_calls']) if stats['connected_calls'] > 0 else 0
    stats['escalation_rate'] = float(calls['escalation_flag'].sum() / stats['connected_calls']) if stats['connected_calls'] > 0 else 0
    stats['ptp_rate'] = float(calls['ptp_flag'].sum() / stats['connected_calls']) if stats['connected_calls'] > 0 else 0
    
    # Intent Stats
    cust_turns = conv[conv['speaker'] == 'Customer'].copy()
    eligible_intents = cust_turns.dropna(subset=['expected_intent_key', 'detected_intent_key'])
    if not eligible_intents.empty:
        correct_preds = (eligible_intents['expected_intent_key'] == eligible_intents['detected_intent_key']).sum()
        stats['intent_accuracy'] = float(correct_preds / len(eligible_intents))
        stats['intent_correct'] = int(correct_preds)
        stats['intent_eligible'] = len(eligible_intents)
        stats['fallback_turns'] = int(cust_turns['fallback_flag'].sum())
    
    # Attempts
    max_attempts = calls.groupby('customer_key')['attempt_number'].max()
    stats['average_max_attempt'] = float(max_attempts.mean()) if not max_attempts.empty else 0
    
    with open('data/validation/statistical_summary.json', 'w') as f:
        json.dump(stats, f, indent=2)
