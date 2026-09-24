import pandas as pd
import matplotlib.pyplot as plt

def run_conversational_ai(df_calls, df_conv):
    res = {}
    
    # 1. Confidence dist
    plt.figure()
    df_conv['confidence_score'].dropna().plot(kind='hist', bins=30)
    plt.title('Confidence Distribution')
    plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_conf_dist.png'); plt.close()
    
    conv_aug = df_conv.merge(df_calls[['call_key', 'bot_name', 'language', 'campaign_name', 'escalation_flag']], on='call_key', how='left')
    
    # 2. Conf by intent
    if conv_aug['expected_intent'].notnull().any():
        plt.figure()
        conv_aug.groupby('expected_intent')['confidence_score'].mean().sort_values().plot(kind='barh')
        plt.title('Confidence by Intent')
        plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_conf_intent.png'); plt.close()
        
    # 3. Conf by bot
    plt.figure()
    conv_aug.groupby('bot_name')['confidence_score'].mean().plot(kind='bar')
    plt.title('Confidence by Bot')
    plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_conf_bot.png'); plt.close()

    # 4. Conf by language
    plt.figure()
    conv_aug.groupby('language')['confidence_score'].mean().plot(kind='bar')
    plt.title('Confidence by Language')
    plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_conf_lang.png'); plt.close()
    
    # 5. Conf by campaign
    plt.figure()
    conv_aug.groupby('campaign_name')['confidence_score'].mean().plot(kind='bar')
    plt.title('Confidence by Campaign')
    plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_conf_camp.png'); plt.close()
    
    # 6. Fallback by conf q
    plt.figure()
    conv_aug['conf_q'] = pd.qcut(conv_aug['confidence_score'], 4, duplicates='drop')
    conv_aug.groupby('conf_q', observed=True)['fallback_flag'].mean().plot(kind='bar')
    plt.title('Fallback by Confidence Quartile')
    plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_conf_fallback.png'); plt.close()

    # Intent accuracy base
    cust_intents = conv_aug[(conv_aug['speaker'] == 'Customer') & (conv_aug['expected_intent_key'].notnull()) & (conv_aug['detected_intent_key'].notnull())].copy()
    cust_intents['is_accurate'] = (cust_intents['expected_intent_key'] == cust_intents['detected_intent_key']).astype(int)
    
    res['intent_denominator'] = len(cust_intents)
    if len(cust_intents) > 0:
        res['intent_accuracy_overall'] = cust_intents['is_accurate'].mean()
        # 7. Accuracy by intent
        plt.figure(figsize=(8,6))
        cust_intents.groupby('expected_intent')['is_accurate'].mean().sort_values().plot(kind='barh')
        plt.title('Accuracy by Intent')
        plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_acc_intent.png'); plt.close()
        
        # 8. Accuracy by bot
        plt.figure()
        cust_intents.groupby('bot_name')['is_accurate'].mean().plot(kind='bar')
        plt.title('Accuracy by Bot')
        plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_acc_bot.png'); plt.close()

        # 9. Accuracy by lang
        plt.figure()
        cust_intents.groupby('language')['is_accurate'].mean().plot(kind='bar')
        plt.title('Accuracy by Language')
        plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_acc_lang.png'); plt.close()

        # 10. Accuracy by campaign
        plt.figure()
        cust_intents.groupby('campaign_name')['is_accurate'].mean().plot(kind='bar')
        plt.title('Accuracy by Campaign')
        plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_acc_camp.png'); plt.close()

    # 11. Fallback by intent
    if conv_aug['expected_intent'].notnull().any():
        plt.figure()
        conv_aug.groupby('expected_intent')['fallback_flag'].mean().sort_values().plot(kind='barh')
        plt.title('Fallback by Intent')
        plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_fb_intent.png'); plt.close()

    # 12. Fallback by bot
    plt.figure()
    conv_aug.groupby('bot_name')['fallback_flag'].mean().plot(kind='bar')
    plt.title('Fallback by Bot')
    plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_fb_bot.png'); plt.close()

    # 13. Sentiment dist
    plt.figure()
    conv_aug['sentiment'].value_counts().plot(kind='bar')
    plt.title('Sentiment Distribution')
    plt.tight_layout(); plt.savefig('artifacts/eda/figures/ai_sent_dist.png'); plt.close()

    return res
