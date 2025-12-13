"""
Mood Analyzer using NLTK VADER Sentiment Analysis
Analyzes user mood descriptions to extract sentiment scores.
"""

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from typing import Dict, Any, Optional


class MoodAnalyzer:
    """
    Analyzes text to extract mood/sentiment using VADER.
    """
    
    # Mood-related keywords to enhance detection
    MOOD_KEYWORDS = {
        'relaxed': ['calm', 'peaceful', 'relaxed', 'chill', 'serene', 'quiet', 'easy', 'lazy'],
        'adventurous': ['adventure', 'exciting', 'thrill', 'action', 'bold', 'daring', 'explosive'],
        'romantic': ['love', 'romantic', 'sweet', 'heart', 'passion', 'tender', 'intimate'],
        'thoughtful': ['think', 'reflect', 'philosophical', 'deep', 'thought', 'ponder', 'intellectual'],
        'excited': ['excited', 'energetic', 'pumped', 'hyped', 'enthusiastic', 'eager', 'thrilled'],
        'melancholic': ['sad', 'melancholy', 'blue', 'down', 'lonely', 'grief', 'sorrow', 'depressed'],
        'curious': ['curious', 'learn', 'discover', 'explore', 'wonder', 'interested', 'fascinating'],
        'escapist': ['escape', 'fantasy', 'different', 'away', 'another world', 'imagination', 'dream'],
        'motivated': ['motivated', 'inspired', 'productive', 'achieve', 'goal', 'success', 'ambition'],
        'contemplative': ['contemplate', 'spiritual', 'meaning', 'life', 'existence', 'mindful', 'zen']
    }
    
    def __init__(self):
        """Initialize the mood analyzer with VADER."""
        self._ensure_vader_downloaded()
        self.sia = SentimentIntensityAnalyzer()
    
    def _ensure_vader_downloaded(self):
        """Ensure VADER lexicon is downloaded."""
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            nltk.download('vader_lexicon', quiet=True)
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text to extract mood information.
        
        Args:
            text: User's mood description
            
        Returns:
            Dictionary with sentiment scores and detected keywords
        """
        if not text or not text.strip():
            return self._empty_result()
        
        text = text.lower().strip()
        
        # Get VADER sentiment scores
        sentiment_scores = self.sia.polarity_scores(text)
        
        # Detect mood keywords
        detected_moods = self._detect_keyword_moods(text)
        
        # Determine overall mood valence
        compound = sentiment_scores['compound']
        if compound >= 0.05:
            valence = 'positive'
        elif compound <= -0.05:
            valence = 'negative'
        else:
            valence = 'neutral'
        
        # Calculate intensity (how strongly the mood is expressed)
        intensity = abs(compound)
        
        return {
            'text': text,
            'compound': compound,
            'positive': sentiment_scores['pos'],
            'negative': sentiment_scores['neg'],
            'neutral': sentiment_scores['neu'],
            'valence': valence,
            'intensity': intensity,
            'detected_moods': detected_moods,
            'primary_mood': detected_moods[0] if detected_moods else None
        }
    
    def _detect_keyword_moods(self, text: str) -> list:
        """
        Detect mood categories based on keywords in text.
        
        Args:
            text: Lowercase text to analyze
            
        Returns:
            List of detected mood categories, sorted by match count
        """
        mood_scores = {}
        
        for mood, keywords in self.MOOD_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                mood_scores[mood] = score
        
        # Sort by score descending
        sorted_moods = sorted(mood_scores.items(), key=lambda x: x[1], reverse=True)
        return [mood for mood, score in sorted_moods]
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty analysis result."""
        return {
            'text': '',
            'compound': 0,
            'positive': 0,
            'negative': 0,
            'neutral': 1,
            'valence': 'neutral',
            'intensity': 0,
            'detected_moods': [],
            'primary_mood': None
        }
    
    def get_mood_summary(self, analysis: Dict[str, Any]) -> str:
        """
        Generate a human-readable mood summary.
        
        Args:
            analysis: Result from analyze()
            
        Returns:
            Summary string
        """
        if not analysis.get('text'):
            return "No mood detected"
        
        valence = analysis['valence']
        intensity = analysis['intensity']
        detected = analysis['detected_moods']
        
        # Intensity description
        if intensity > 0.5:
            intensity_desc = "strongly"
        elif intensity > 0.2:
            intensity_desc = "moderately"
        else:
            intensity_desc = "slightly"
        
        # Build summary
        if detected:
            mood_list = ', '.join(detected[:3])
            return f"Feeling {intensity_desc} {valence} with {mood_list} vibes"
        else:
            return f"Feeling {intensity_desc} {valence}"


# Singleton instance
_analyzer: Optional[MoodAnalyzer] = None

def get_mood_analyzer() -> MoodAnalyzer:
    """Get or create the mood analyzer singleton."""
    global _analyzer
    if _analyzer is None:
        _analyzer = MoodAnalyzer()
    return _analyzer
