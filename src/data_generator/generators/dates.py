import pandas as pd
from src.data_generator.config import config

def generate_dates():
    start_date = config.dataset.get('start_date', '2026-01-01')
    end_date = config.dataset.get('end_date', '2026-06-30')
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    df = pd.DataFrame({'date': date_range})
    df['date_key'] = df['date'].dt.strftime('%Y%m%d').astype(int)
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['week'] = df['date'].dt.isocalendar().week.astype(int)
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.month_name()
    df['month_number'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['year'] = df['date'].dt.year
    
    # IND FY (Apr-Mar)
    def get_financial_year(dt):
        if dt.month >= 4:
            return f"FY{str(dt.year)[-2:]}-{str(dt.year+1)[-2:]}"
        else:
            return f"FY{str(dt.year-1)[-2:]}-{str(dt.year)[-2:]}"
            
    df['financial_year'] = df['date'].apply(get_financial_year)
    df['is_weekend'] = df['date'].dt.dayofweek.isin([5, 6]).astype(int)
    
    # Reorder based on dictionary
    cols = ['date_key', 'date', 'day', 'day_name', 'week', 'month', 'month_name', 
            'month_number', 'quarter', 'year', 'financial_year', 'is_weekend']
    
    return df[cols]
