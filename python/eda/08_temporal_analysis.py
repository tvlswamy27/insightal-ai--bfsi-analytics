import pandas as pd
import matplotlib.pyplot as plt

def run_temporal(df_calls):
    df_calls['full_date'] = pd.to_datetime(df_calls['full_date'])
    df_calls['year_month'] = df_calls['full_date'].dt.to_period('M').astype(str)
    df_calls['year_week'] = df_calls['full_date'].dt.to_period('W').astype(str)
    
    def get_metrics(grouped):
        return {
            'volume': grouped.size(),
            'connection_rate': grouped['connection_status'].apply(lambda x: (x=='Connected').mean()),
            'containment_rate': grouped['containment_flag'].mean(),
            'escalation_rate': grouped['escalation_flag'].mean(),
            'resolution_rate': grouped['resolution_flag'].mean(),
            'ptp_rate': grouped['ptp_flag'].mean(),
            'payment_amount': grouped['payment_amount'].sum()
        }
    
    daily = df_calls.groupby('full_date')
    weekly = df_calls.groupby('year_week')
    monthly = df_calls.groupby('year_month')
    
    d_metrics = get_metrics(daily)
    w_metrics = get_metrics(weekly)
    m_metrics = get_metrics(monthly)
    
    daily_stats = {}
    weekly_stats = {}
    monthly_stats = {}
    
    # Generate 7 plots for daily vs rolling average
    for name, s in d_metrics.items():
        s_dict = s.copy()
        s_dict.index = s_dict.index.astype(str)
        daily_stats[name] = s_dict.to_dict()
        
        plt.figure(figsize=(10,5))
        s.plot(label='Daily', alpha=0.5)
        s.rolling(7).mean().plot(label='7-Day Rolling', linewidth=2)
        plt.title(f'Daily {name}')
        plt.legend()
        plt.tight_layout(); plt.savefig(f'artifacts/eda/figures/time_{name}.png'); plt.close()
        
    for name, s in w_metrics.items():
        s_dict = s.copy()
        s_dict.index = s_dict.index.astype(str)
        weekly_stats[name] = s_dict.to_dict()
        
    for name, s in m_metrics.items():
        s_dict = s.copy()
        s_dict.index = s_dict.index.astype(str)
        monthly_stats[name] = s_dict.to_dict()

    return {"daily_stats": daily_stats, "weekly_stats": weekly_stats, "monthly_stats": monthly_stats}
