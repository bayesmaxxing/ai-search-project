# This is to create a first draft of sentiment analysis of brand mentions
from textblob import TextBlob


class SentimentAnalysis:
    def __init__(self):
        pass

    def predict_sentiment(self, texts):
        sentiments = []
        for text in texts:
            analysis = TextBlob(text)
            # Convert polarity (-1 to 1) to our 5 categories
            polarity = analysis.sentiment.polarity
            if polarity <= -0.6:
                sentiment = "Very Negative"
            elif polarity <= -0.2:
                sentiment = "Negative"
            elif polarity <= 0.2:
                sentiment = "Neutral"
            elif polarity <= 0.6:
                sentiment = "Positive"
            else:
                sentiment = "Very Positive"
            sentiments.append(sentiment)
        return sentiments


def main():
    sentiment_analysis = SentimentAnalysis()
    texts = ["I love this product", "I hate this product", "I'm neutral about this product"]
    for text, sentiment in zip(texts, sentiment_analysis.predict_sentiment(texts)):
        print(f"Text: {text}\nSentiment: {sentiment}\n")

if __name__ == "__main__":
    main()
