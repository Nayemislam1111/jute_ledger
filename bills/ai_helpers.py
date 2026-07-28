# ai_helpers.py
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from .models import JuteRate

def update_area_forecasting(area_name):
    """
    নির্দিষ্ট এরিয়ার আগের সব রেট অ্যানালাইসিস করে আগামী রেট প্রেডিক্ট করে 
    এবং সর্বশেষ রেট অবজেক্টে ডেটা আপডেট করে।
    """
    # নির্দিষ্ট এরিয়ার সব রেট ওল্ড থেকে নিউ অর্ডারে আনা হলো
    rates = JuteRate.objects.filter(area__iexact=area_name.strip()).order_by('effect_date')
    
    # টাইম সিরিজ ফোরকাস্টিং এর জন্য ন্যূনতম ৩টি ভিন্ন তারিখের রেট ডেটাবেসে থাকা লাগবে
    if rates.count() < 3:
        return
        
    # পান্ডাস ডাটাফ্রেমে রূপান্তর
    data = {
        'date': [r.effect_date for r in rates],
        'c_rate': [r.c_rate for r in rates] # এখানে C Rate এর ওপর ভিত্তি করে ট্রেন করা হচ্ছে
    }
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    
    try:
        # ARIMA মডেল দিয়ে আগামী রেট প্রেডিকশন
        model = ARIMA(df['c_rate'], order=(1, 1, 0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=1)
        predicted_val = float(forecast.iloc[0])
        
        # সহজ একটি কনফিডেন্স স্কোর লজিক (ডেটা বৃদ্ধির সাথে সাথে স্কোর বাড়ে)
        confidence = min(96.5, 65.0 + (rates.count() * 2.5))
        
        # সর্বশেষ এন্ট্রি করা রেটে প্রেডিকশন ডেটা সেভ করা হচ্ছে
        latest_rate = rates.last() # যেহেতু effect_date দিয়ে এসেন্ডিং করা ছিল
        if latest_rate:
            latest_rate.predicted_next_rate = round(predicted_val, 2)
            latest_rate.ai_confidence_score = round(confidence, 2)
            latest_rate.save()
            
    except Exception as e:
        print(f"Forecasting Engine Error for {area_name}: {e}")