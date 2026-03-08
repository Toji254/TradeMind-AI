from __future__ import annotations

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


analyzer = SentimentIntensityAnalyzer()


def score_text(text: str) -> dict[str, float]:
    return analyzer.polarity_scores(text)
