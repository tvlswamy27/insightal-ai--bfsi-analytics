import pandas as pd
from src.data_generator.random_state import get_rng
from src.data_generator.config import config

def generate_bots():
    bots = [
        {'bot_id': 'BOT_V1_EN', 'bot_name': 'Insightal Voice', 'bot_version': 'v1.0', 'language': 'English', 'model_type': 'Generative', 'deployment_date': '2025-01-01', 'performance_modifier': -0.1},
        {'bot_id': 'BOT_V1_HI', 'bot_name': 'Insightal Voice', 'bot_version': 'v1.0', 'language': 'Hindi', 'model_type': 'Generative', 'deployment_date': '2025-01-01', 'performance_modifier': 0.0},
        {'bot_id': 'BOT_V1.1_EN', 'bot_name': 'Insightal Voice', 'bot_version': 'v1.1', 'language': 'English', 'model_type': 'Generative', 'deployment_date': '2026-03-01', 'performance_modifier': 0.2},
        {'bot_id': 'BOT_V2_EN', 'bot_name': 'Insightal Voice Pro', 'bot_version': 'v2.0', 'language': 'English', 'model_type': 'Generative', 'deployment_date': '2026-05-01', 'performance_modifier': 0.4},
        {'bot_id': 'BOT_V1_TE', 'bot_name': 'Insightal Voice', 'bot_version': 'v1.0', 'language': 'Telugu', 'model_type': 'Generative', 'deployment_date': '2025-06-01', 'performance_modifier': -0.05},
        {'bot_id': 'BOT_V1_TA', 'bot_name': 'Insightal Voice', 'bot_version': 'v1.0', 'language': 'Tamil', 'model_type': 'Generative', 'deployment_date': '2025-06-01', 'performance_modifier': -0.05},
    ]
    
    df = pd.DataFrame(bots)
    df.insert(0, 'bot_key', range(1, len(df) + 1))
    df['deployment_date'] = pd.to_datetime(df['deployment_date']).dt.date
    return df
