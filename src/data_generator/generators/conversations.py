import pandas as pd
import numpy as np
from src.data_generator.random_state import get_rng
from src.data_generator.utils.ids import generate_uuids
from src.data_generator.models.behavioral_model import logistic_probability

def generate_conversations(calls, intents, bots):
    rng = get_rng()
    
    connected_calls = calls[calls['connection_status'] == 'Connected'].copy()
    num_connected = len(connected_calls)
    
    if num_connected == 0:
        return pd.DataFrame()
        
    intent_indices = rng.choice(len(intents), size=num_connected)
    chosen_intents = intents.iloc[intent_indices].reset_index(drop=True)
    connected_calls['expected_call_intent_key'] = chosen_intents['intent_key'].values
    connected_calls['base_difficulty'] = chosen_intents['base_difficulty'].values
    
    bot_perf = bots.set_index('bot_key')['performance_modifier'].to_dict()
    connected_calls['bot_modifier'] = connected_calls['bot_key'].map(bot_perf)
    
    turns_data = []
    
    for idx, row in connected_calls.iterrows():
        call_id = row['call_id']
        call_key = row['call_key']
        call_start = row['call_start_time']
        
        dpd_effect = min(row['days_past_due_at_call'] / 100.0, 1.0)
        bot_eff = row['bot_modifier']
        
        latent_difficulty = row['base_difficulty'] + dpd_effect * 0.5 - bot_eff
        
        num_customer_turns = int(rng.integers(1, 6))
        if latent_difficulty > 0.8:
            num_customer_turns += rng.integers(1, 3) 
            
        current_time = call_start + pd.Timedelta(seconds=rng.integers(1, 5))
        turn_number = 1
        
        for t in range(num_customer_turns):
            turns_data.append({
                'turn_id': generate_uuids(1)[0],
                'conversation_id': call_id,
                'call_key': call_key,
                'turn_number': turn_number,
                'speaker': 'Bot',
                'timestamp': current_time,
                'utterance': f"Bot generated utterance {turn_number}",
                'expected_intent_key': None,
                'detected_intent_key': None,
                'confidence_score': None,
                'sentiment': None,
                'sentiment_score': None,
                'fallback_flag': 0,
                'escalation_trigger_flag': 0
            })
            current_time += pd.Timedelta(seconds=rng.integers(2, 10))
            turn_number += 1
            
            conf_logit = 2.0 - latent_difficulty * 3.0
            confidence = logistic_probability(conf_logit, [0], noise_scale=0.5, rng=rng)
            
            sent_logit = 1.0 - latent_difficulty * 2.0
            sent_prob = logistic_probability(sent_logit, [0], noise_scale=0.5, rng=rng)
            sentiment_score = (sent_prob * 2) - 1 
            
            if sentiment_score > 0.3:
                sentiment = 'Positive'
            elif sentiment_score < -0.3:
                sentiment = 'Negative'
            else:
                sentiment = 'Neutral'
                
            fb_logit = -2.0 + (1.0 - confidence) * 4.0
            fb_prob = logistic_probability(fb_logit, [0], noise_scale=0.5, rng=rng)
            is_fallback = 1 if rng.random() < fb_prob else 0
            
            accuracy_logit = -1.0 + confidence * 4.0
            accuracy_prob = logistic_probability(accuracy_logit, [0], noise_scale=0.5, rng=rng)
            is_correct = 1 if rng.random() < accuracy_prob else 0
            
            if is_fallback:
                detected_intent = None
            elif is_correct:
                detected_intent = row['expected_call_intent_key']
            else:
                num_intents = len(intents)
                confused_intent = rng.integers(1, num_intents + 1)
                detected_intent = confused_intent if confused_intent != row['expected_call_intent_key'] else (confused_intent % num_intents) + 1
            
            
            turns_data.append({
                'turn_id': generate_uuids(1)[0],
                'conversation_id': call_id,
                'call_key': call_key,
                'turn_number': turn_number,
                'speaker': 'Customer',
                'timestamp': current_time,
                'utterance': f"Customer utterance {turn_number}",
                'expected_intent_key': row['expected_call_intent_key'],
                'detected_intent_key': detected_intent,
                'confidence_score': confidence,
                'sentiment': sentiment,
                'sentiment_score': sentiment_score,
                'fallback_flag': is_fallback,
                'escalation_trigger_flag': 0 
            })
            current_time += pd.Timedelta(seconds=rng.integers(2, 15))
            turn_number += 1
            
    df_turns = pd.DataFrame(turns_data)
    if not df_turns.empty:
        df_turns.insert(0, 'turn_key', range(1, len(df_turns) + 1))
    return df_turns
