"""
Mood Classifier
Maps sentiment analysis to mood categories and suggests matching genres.
"""

from typing import Dict, List, Any, Optional, Tuple
from .mood_analyzer import MoodAnalyzer, get_mood_analyzer


class MoodClassifier:
    """
    Classifies user mood and maps to suitable book genres.
    """
    
    # The 10 mood categories with associated genres and characteristics
    MOOD_CATEGORIES = {
        'relaxed': {
            'description': 'Calm, peaceful, seeking comfort',
            'genres': ['Contemporary Fiction', 'Cozy Mystery', 'Slice of Life', 'Light Romance', 'Humor'],
            'keywords': ['calm', 'peaceful', 'relaxed', 'chill', 'cozy', 'easy', 'lazy', 'comfort'],
            'valence_weight': 0.3,  # Slightly positive
            'intensity_range': (0, 0.4)  # Low intensity
        },
        'adventurous': {
            'description': 'Seeking excitement, action, and thrills',
            'genres': ['Adventure', 'Action', 'Thriller', 'Science Fiction', 'Fantasy'],
            'keywords': ['adventure', 'exciting', 'thrill', 'action', 'explore', 'brave', 'bold'],
            'valence_weight': 0.5,  # Positive
            'intensity_range': (0.3, 1.0)  # Medium to high intensity
        },
        'romantic': {
            'description': 'Feeling loving, seeking emotional connection',
            'genres': ['Romance', 'Contemporary Romance', 'Historical Romance', 'Romantic Comedy', 'Drama'],
            'keywords': ['love', 'romantic', 'heart', 'passion', 'sweet', 'tender', 'relationship'],
            'valence_weight': 0.4,  # Positive
            'intensity_range': (0.2, 0.8)  # Medium intensity
        },
        'thoughtful': {
            'description': 'In a reflective, analytical mood',
            'genres': ['Literary Fiction', 'Philosophy', 'Non-fiction', 'Psychology', 'Essays'],
            'keywords': ['think', 'reflect', 'philosophical', 'intellectual', 'ponder', 'analytical'],
            'valence_weight': 0.0,  # Neutral
            'intensity_range': (0.1, 0.6)  # Low to medium intensity
        },
        'excited': {
            'description': 'Energetic, enthusiastic, ready for something big',
            'genres': ['Thriller', 'Science Fiction', 'Fantasy', 'Adventure', 'Horror'],
            'keywords': ['excited', 'energetic', 'pumped', 'hyped', 'enthusiastic', 'eager'],
            'valence_weight': 0.7,  # Very positive
            'intensity_range': (0.5, 1.0)  # High intensity
        },
        'melancholic': {
            'description': 'Feeling sad, contemplating loss or loneliness',
            'genres': ['Literary Fiction', 'Drama', 'Poetry', 'Biography', 'Historical Fiction'],
            'keywords': ['sad', 'melancholy', 'lonely', 'grief', 'sorrow', 'blue', 'down'],
            'valence_weight': -0.5,  # Negative
            'intensity_range': (0.2, 0.8)  # Medium intensity
        },
        'curious': {
            'description': 'Eager to learn, discover, explore ideas',
            'genres': ['Non-fiction', 'Science', 'History', 'Biography', 'Mystery', 'True Crime'],
            'keywords': ['curious', 'learn', 'discover', 'wonder', 'explore', 'interested'],
            'valence_weight': 0.3,  # Slightly positive
            'intensity_range': (0.2, 0.7)  # Medium intensity
        },
        'escapist': {
            'description': 'Wanting to leave reality behind',
            'genres': ['Fantasy', 'Science Fiction', 'Magical Realism', 'Adventure', 'Historical Fiction'],
            'keywords': ['escape', 'fantasy', 'different', 'away', 'another world', 'dream'],
            'valence_weight': 0.0,  # Neutral (can be positive or negative)
            'intensity_range': (0.3, 0.9)  # Medium to high intensity
        },
        'motivated': {
            'description': 'Feeling driven, seeking inspiration and growth',
            'genres': ['Self-help', 'Biography', 'Business', 'Personal Development', 'Psychology'],
            'keywords': ['motivated', 'inspired', 'achieve', 'goal', 'success', 'growth', 'improve'],
            'valence_weight': 0.6,  # Positive
            'intensity_range': (0.4, 1.0)  # Medium to high intensity
        },
        'contemplative': {
            'description': 'Seeking meaning, spiritual depth',
            'genres': ['Philosophy', 'Spirituality', 'Poetry', 'Literary Fiction', 'Meditation'],
            'keywords': ['contemplate', 'spiritual', 'meaning', 'life', 'existence', 'mindful'],
            'valence_weight': 0.1,  # Slightly positive
            'intensity_range': (0.1, 0.5)  # Low to medium intensity
        }
    }
    
    def __init__(self):
        """Initialize the mood classifier."""
        self.analyzer = get_mood_analyzer()
    
    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classify user mood from text description.
        
        Args:
            text: User's mood description
            
        Returns:
            Classification result with mood category, confidence, and suggested genres
        """
        # Get sentiment analysis
        analysis = self.analyzer.analyze(text)
        
        if not text or not text.strip():
            return self._default_classification()
        
        # Score each mood category
        mood_scores = {}
        
        for mood_name, mood_data in self.MOOD_CATEGORIES.items():
            score = self._calculate_mood_score(text.lower(), analysis, mood_name, mood_data)
            mood_scores[mood_name] = score
        
        # Get top moods
        sorted_moods = sorted(mood_scores.items(), key=lambda x: x[1], reverse=True)
        top_mood = sorted_moods[0]
        
        # Calculate confidence
        total_score = sum(mood_scores.values())
        confidence = top_mood[1] / total_score if total_score > 0 else 0
        
        # Get suggested genres (combine from top moods)
        suggested_genres = self._get_genre_suggestions(sorted_moods[:3])
        
        return {
            'primary_mood': top_mood[0],
            'mood_description': self.MOOD_CATEGORIES[top_mood[0]]['description'],
            'confidence': round(confidence, 2),
            'mood_scores': {k: round(v, 3) for k, v in sorted_moods},
            'secondary_moods': [m[0] for m in sorted_moods[1:3]],
            'suggested_genres': suggested_genres,
            'sentiment': {
                'valence': analysis['valence'],
                'intensity': round(analysis['intensity'], 2),
                'compound': round(analysis['compound'], 2)
            },
            'original_text': text
        }
    
    def _calculate_mood_score(self, text: str, analysis: Dict, mood_name: str, mood_data: Dict) -> float:
        """
        Calculate score for a specific mood category.
        
        Args:
            text: Lowercase input text
            analysis: Sentiment analysis result
            mood_name: Name of the mood category
            mood_data: Mood category configuration
            
        Returns:
            Score for this mood category
        """
        score = 0.0
        
        # Keyword matching (40% weight)
        keywords = mood_data['keywords']
        keyword_matches = sum(1 for kw in keywords if kw in text)
        keyword_score = min(keyword_matches / 3, 1.0)  # Cap at 1.0
        score += keyword_score * 0.4
        
        # Valence matching (30% weight)
        expected_valence = mood_data['valence_weight']
        actual_compound = analysis['compound']
        valence_diff = abs(expected_valence - actual_compound)
        valence_score = max(0, 1 - valence_diff)
        score += valence_score * 0.3
        
        # Intensity matching (20% weight)
        intensity = analysis['intensity']
        min_int, max_int = mood_data['intensity_range']
        if min_int <= intensity <= max_int:
            intensity_score = 1.0
        else:
            # Partial score for close matches
            if intensity < min_int:
                intensity_score = max(0, 1 - (min_int - intensity) * 2)
            else:
                intensity_score = max(0, 1 - (intensity - max_int) * 2)
        score += intensity_score * 0.2
        
        # Check if detected by mood analyzer (10% bonus)
        if mood_name in analysis.get('detected_moods', []):
            score += 0.1
        
        return score
    
    def _get_genre_suggestions(self, top_moods: List[Tuple[str, float]]) -> List[str]:
        """
        Get genre suggestions from top mood matches.
        
        Args:
            top_moods: List of (mood_name, score) tuples
            
        Returns:
            Ordered list of suggested genres
        """
        genre_scores = {}
        
        for mood_name, mood_score in top_moods:
            mood_data = self.MOOD_CATEGORIES[mood_name]
            genres = mood_data['genres']
            
            # Higher scored moods contribute more to genre scores
            for i, genre in enumerate(genres):
                # Earlier genres in list are more relevant
                genre_weight = mood_score * (1 - i * 0.1)
                if genre in genre_scores:
                    genre_scores[genre] = max(genre_scores[genre], genre_weight)
                else:
                    genre_scores[genre] = genre_weight
        
        # Sort and return top genres
        sorted_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)
        return [genre for genre, score in sorted_genres[:7]]
    
    def _default_classification(self) -> Dict[str, Any]:
        """Return default classification when no mood detected."""
        return {
            'primary_mood': 'curious',
            'mood_description': 'Open to discovery',
            'confidence': 0.0,
            'mood_scores': {mood: 0.1 for mood in self.MOOD_CATEGORIES},
            'secondary_moods': ['thoughtful', 'adventurous'],
            'suggested_genres': ['Fiction', 'Non-fiction', 'Mystery', 'Fantasy', 'Literary Fiction'],
            'sentiment': {'valence': 'neutral', 'intensity': 0, 'compound': 0},
            'original_text': ''
        }
    
    def get_all_moods(self) -> List[Dict[str, Any]]:
        """Get list of all mood categories with descriptions."""
        return [
            {
                'name': name,
                'description': data['description'],
                'genres': data['genres']
            }
            for name, data in self.MOOD_CATEGORIES.items()
        ]


# Singleton instance
_classifier: Optional[MoodClassifier] = None

def get_mood_classifier() -> MoodClassifier:
    """Get or create the mood classifier singleton."""
    global _classifier
    if _classifier is None:
        _classifier = MoodClassifier()
    return _classifier
