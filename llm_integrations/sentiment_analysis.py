# This is to create a first draft of sentiment analysis of brand mentions
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


class SentimentAnalysis:
    def __init__(self, model_name="tabularisai/multilingual-sentiment-analysis"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

    def predict_sentiment(self, texts):
        inputs = self.tokenizer(texts, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
            sentiment_map = {0: "Very Negative", 1: "Negative", 2: "Neutral", 3: "Positive", 4: "Very Positive"}
        return [sentiment_map[p] for p in torch.argmax(probabilities, dim=-1).tolist()]


def main():
    sentiment_analysis = SentimentAnalysis()
    texts = ["I love this product", "I hate this product", "I'm neutral about this product"]
    for text, sentiment in zip(texts, sentiment_analysis.predict_sentiment(texts)):
        print(f"Text: {text}\nSentiment: {sentiment}\n")

if __name__ == "__main__":
    main()
