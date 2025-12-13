"""
Book Scorer
Multi-factor scoring system for book recommendations.
"""

from typing import Dict, List, Any, Optional
from fuzzywuzzy import fuzz


class BookScorer:
    """
    Scores books based on multiple factors for recommendations.
    
    Scoring weights:
    - Mood match: 40%
    - Genre preference: 25%
    - Reading history: 15%
    - Reading difficulty: 10%
    - Popularity/rating: 10%
    """
    
    # Scoring weights
    WEIGHTS = {
        'mood_match': 0.40,
        'genre_preference': 0.25,
        'reading_history': 0.15,
        'difficulty': 0.10,
        'popularity': 0.10
    }
    
    # Page count ranges for difficulty estimation
    DIFFICULTY_RANGES = {
        'easy': (0, 200),
        'medium': (200, 400),
        'challenging': (400, 600),
        'difficult': (600, float('inf'))
    }
    
    # Mood to difficulty preference mapping
    MOOD_DIFFICULTY_PREFERENCE = {
        'relaxed': 'easy',
        'adventurous': 'medium',
        'romantic': 'easy',
        'thoughtful': 'challenging',
        'excited': 'medium',
        'melancholic': 'medium',
        'curious': 'challenging',
        'escapist': 'medium',
        'motivated': 'medium',
        'contemplative': 'medium'
    }
    
    def __init__(self):
        """Initialize the book scorer."""
        self.genre_preferences: Dict[str, float] = {}
        self.reading_history: List[str] = []
    
    def set_user_preferences(self, genre_preferences: Dict[str, float] = None, 
                            reading_history: List[str] = None):
        """
        Set user preferences for scoring.
        
        Args:
            genre_preferences: Dict of genre -> preference score (0-1)
            reading_history: List of previously read book titles
        """
        if genre_preferences:
            self.genre_preferences = genre_preferences
        if reading_history:
            self.reading_history = reading_history
    
    def score_books(self, books: List[Dict[str, Any]], 
                   mood_classification: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Score a list of books based on mood and other factors.
        
        Args:
            books: List of book metadata dictionaries
            mood_classification: Result from MoodClassifier.classify()
            
        Returns:
            List of books with scores, sorted by total score descending
        """
        scored_books = []
        suggested_genres = mood_classification.get('suggested_genres', [])
        primary_mood = mood_classification.get('primary_mood', 'curious')
        
        for book in books:
            scores = self._calculate_scores(book, suggested_genres, primary_mood)
            
            # Calculate weighted total
            total_score = sum(
                scores[factor] * weight 
                for factor, weight in self.WEIGHTS.items()
            )
            
            scored_book = book.copy()
            scored_book['scores'] = scores
            scored_book['total_score'] = round(total_score, 3)
            scored_book['score_percentage'] = round(total_score * 100, 1)
            scored_books.append(scored_book)
        
        # Sort by total score descending
        scored_books.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Add rank
        for i, book in enumerate(scored_books):
            book['rank'] = i + 1
        
        return scored_books
    
    def _calculate_scores(self, book: Dict[str, Any], 
                         suggested_genres: List[str],
                         primary_mood: str) -> Dict[str, float]:
        """
        Calculate individual factor scores for a book.
        
        Args:
            book: Book metadata
            suggested_genres: Genres suggested by mood classifier
            primary_mood: The primary detected mood
            
        Returns:
            Dictionary of factor scores
        """
        return {
            'mood_match': self._score_mood_match(book, suggested_genres),
            'genre_preference': self._score_genre_preference(book),
            'reading_history': self._score_reading_history(book),
            'difficulty': self._score_difficulty(book, primary_mood),
            'popularity': self._score_popularity(book)
        }
    
    def _score_mood_match(self, book: Dict[str, Any], 
                         suggested_genres: List[str]) -> float:
        """
        Score how well book matches mood-suggested genres.
        
        Args:
            book: Book metadata
            suggested_genres: Genres suggested by mood
            
        Returns:
            Score from 0 to 1
        """
        if not suggested_genres:
            return 0.5  # Neutral if no mood genres
        
        book_genres = book.get('genres', [])
        if isinstance(book_genres, str):
            book_genres = [book_genres]
        
        if not book_genres:
            book_genres = [book.get('genre', 'Unknown')]
        
        # Calculate best match using fuzzy matching
        best_match = 0
        for book_genre in book_genres:
            for i, suggested_genre in enumerate(suggested_genres):
                # Position weight - earlier suggestions are more relevant
                position_weight = 1 - (i * 0.1)
                match_score = fuzz.ratio(book_genre.lower(), suggested_genre.lower()) / 100
                weighted_score = match_score * position_weight
                best_match = max(best_match, weighted_score)
        
        return min(best_match, 1.0)
    
    def _score_genre_preference(self, book: Dict[str, Any]) -> float:
        """
        Score based on user's genre preferences.
        
        Args:
            book: Book metadata
            
        Returns:
            Score from 0 to 1
        """
        if not self.genre_preferences:
            return 0.5  # Neutral if no preferences set
        
        book_genres = book.get('genres', [])
        if isinstance(book_genres, str):
            book_genres = [book_genres]
        
        if not book_genres:
            return 0.5
        
        # Find best matching genre preference
        best_score = 0
        for book_genre in book_genres:
            for pref_genre, pref_score in self.genre_preferences.items():
                match = fuzz.ratio(book_genre.lower(), pref_genre.lower()) / 100
                if match > 0.7:  # Consider it a match if >70% similar
                    best_score = max(best_score, pref_score)
        
        return best_score if best_score > 0 else 0.5
    
    def _score_reading_history(self, book: Dict[str, Any]) -> float:
        """
        Score based on reading history (penalize already read books).
        
        Args:
            book: Book metadata
            
        Returns:
            Score from 0 to 1
        """
        if not self.reading_history:
            return 0.8  # High score if no history (novel books)
        
        book_title = book.get('title', '').lower()
        
        # Check if already read
        for read_title in self.reading_history:
            if fuzz.ratio(book_title, read_title.lower()) > 85:
                return 0.2  # Low score for already read books
        
        return 0.8  # Good score for unread books
    
    def _score_difficulty(self, book: Dict[str, Any], primary_mood: str) -> float:
        """
        Score based on reading difficulty match with mood.
        
        Args:
            book: Book metadata
            primary_mood: Detected mood
            
        Returns:
            Score from 0 to 1
        """
        page_count = book.get('page_count', 0)
        
        if page_count <= 0:
            return 0.5  # Neutral if unknown
        
        # Determine book difficulty
        book_difficulty = 'medium'
        for difficulty, (min_pages, max_pages) in self.DIFFICULTY_RANGES.items():
            if min_pages <= page_count < max_pages:
                book_difficulty = difficulty
                break
        
        # Get preferred difficulty for mood
        preferred_difficulty = self.MOOD_DIFFICULTY_PREFERENCE.get(primary_mood, 'medium')
        
        # Score based on match
        difficulty_order = ['easy', 'medium', 'challenging', 'difficult']
        book_idx = difficulty_order.index(book_difficulty)
        pref_idx = difficulty_order.index(preferred_difficulty)
        
        diff = abs(book_idx - pref_idx)
        scores = {0: 1.0, 1: 0.7, 2: 0.4, 3: 0.2}
        
        return scores.get(diff, 0.5)
    
    def _score_popularity(self, book: Dict[str, Any]) -> float:
        """
        Score based on book's rating and popularity.
        
        Args:
            book: Book metadata
            
        Returns:
            Score from 0 to 1
        """
        rating = book.get('rating', 0)
        ratings_count = book.get('ratings_count', 0)
        
        if rating <= 0:
            return 0.5  # Neutral if no rating
        
        # Normalize rating (assuming 5-star scale)
        rating_score = rating / 5.0
        
        # Bonus for well-reviewed books (many ratings)
        popularity_bonus = min(ratings_count / 10000, 0.2)  # Max 0.2 bonus
        
        return min(rating_score + popularity_bonus, 1.0)


# Singleton instance
_scorer: Optional[BookScorer] = None

def get_book_scorer() -> BookScorer:
    """Get or create the book scorer singleton."""
    global _scorer
    if _scorer is None:
        _scorer = BookScorer()
    return _scorer
