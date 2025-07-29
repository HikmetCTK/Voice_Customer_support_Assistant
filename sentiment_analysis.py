# Kolay kullanım için pipeline 
from transformers.pipelines import pipeline

pipe = pipeline("text-classification", model="saribasmetehan/bert-base-turkish-sentiment-analysis")

def analyze_sentiment(text): # label 1 = positive, label 0 = nötr label 2 = negative
    result = pipe(text)
    return result


def categorize_sentiment(text):
    result = analyze_sentiment(text)
    label = result[0]['label']
    
    if label == 'LABEL_1':
        return "positive"
    elif label == 'LABEL_0':
        return "neutral"
    elif label == 'LABEL_2':
        return "negative"
    else:
        return None
