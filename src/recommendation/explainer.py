"""
Recommendation Explainer
Generates human-readable explanations for book recommendations.
"""

from typing import Dict, List, Any, Optional


class RecommendationExplainer:
    """
    Generates explanations for why a book was recommended.
    """
    
    # Templates for different score factors
    EXPLANATION_TEMPLATES = {
        'mood_match': {
            'high': "This {genre} book perfectly matches your {mood} mood",
            'medium': "The {genre} themes align well with how you're feeling",
            'low': "While not a perfect mood match, this book offers variety"
        },
        'genre_preference': {
            'high': "You've shown a preference for {genre} books",
            'medium': "This genre fits your reading tastes",
            'low': "This might expand your reading horizons"
        },
        'reading_history': {
            'high': "A fresh read you haven't explored yet",
            'medium': "Something new for your reading list",
            'low': "You may have read something similar before"
        },
        'difficulty': {
            'high': "The length is just right for your current mood",
            'medium': "A comfortable read that won't overwhelm",
            'low': "This might be more challenging than you prefer right now"
        },
        'popularity': {
            'high': "Highly rated by readers ({rating}⭐)",
            'medium': "Well-received by readers",
            'low': "A hidden gem waiting to be discovered"
        }
    }
    
    # Mood-specific phrases
    MOOD_PHRASES = {
        'relaxed': ['perfect for unwinding', 'a cozy read', 'gentle and soothing'],
        'adventurous': ['full of excitement', 'thrilling journey', 'action-packed'],
        'romantic': ['heartwarming', 'touching', 'emotionally rich'],
        'thoughtful': ['intellectually stimulating', 'thought-provoking', 'deep'],
        'excited': ['energizing', 'page-turner', 'keeps you on the edge'],
        'melancholic': ['beautifully melancholic', 'emotionally resonant', 'deeply moving'],
        'curious': ['enlightening', 'fascinating', 'opens new perspectives'],
        'escapist': ['transports you', 'immersive world', 'perfect escape'],
        'motivated': ['inspiring', 'empowering', 'motivational'],
        'contemplative': ['meditative', 'peaceful', 'spiritually enriching']
    }
    
    def __init__(self):
        """Initialize the explainer."""
        pass
    
    def explain(self, book: Dict[str, Any], 
               mood_classification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate explanation for a book recommendation.
        
        Args:
            book: Book with scores
            mood_classification: Mood classification result
            
        Returns:
            Dictionary with explanation text and breakdown
        """
        scores = book.get('scores', {})
        primary_mood = mood_classification.get('primary_mood', 'curious')
        
        # Generate factor explanations
        factor_explanations = []
        
        for factor, score in scores.items():
            level = self._get_score_level(score)
            template = self.EXPLANATION_TEMPLATES.get(factor, {}).get(level, '')
            
            if template:
                explanation = self._format_template(template, book, primary_mood, score)
                factor_explanations.append({
                    'factor': factor,
                    'score': score,
                    'level': level,
                    'explanation': explanation
                })
        
        # Sort by score descending
        factor_explanations.sort(key=lambda x: x['score'], reverse=True)
        
        # Generate main explanation
        main_explanation = self._generate_main_explanation(
            book, primary_mood, factor_explanations
        )
        
        # Generate short summary
        summary = self._generate_summary(book, primary_mood, factor_explanations)
        
        return {
            'main_explanation': main_explanation,
            'summary': summary,
            'factor_breakdown': factor_explanations,
            'mood_phrase': self._get_mood_phrase(primary_mood),
            'match_percentage': book.get('score_percentage', 0)
        }
    
    def _get_score_level(self, score: float) -> str:
        """Convert numeric score to level category."""
        if score >= 0.7:
            return 'high'
        elif score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _format_template(self, template: str, book: Dict[str, Any], 
                        mood: str, score: float) -> str:
        """Format a template with book and mood data."""
        genre = book.get('genre', 'Fiction')
        if isinstance(genre, list):
            genre = genre[0] if genre else 'Fiction'
        
        rating = book.get('rating', 0)
        rating_str = f"{rating:.1f}" if rating else "N/A"
        
        return template.format(
            genre=genre,
            mood=mood,
            rating=rating_str,
            title=book.get('title', 'This book'),
            author=book.get('author', 'Unknown')
        )
    
    def _generate_main_explanation(self, book: Dict[str, Any], 
                                   mood: str,
                                   factors: List[Dict]) -> str:
        """Generate the main explanation paragraph."""
        title = book.get('title', 'This book')
        author = book.get('author', 'the author')
        score_pct = book.get('score_percentage', 0)
        
        # Get top factors
        top_factors = [f for f in factors if f['level'] == 'high'][:2]
        
        # Build explanation
        parts = []
        
        # Opening with score
        parts.append(f"**{title}** by {author} is a {score_pct}% match for you.")
        
        # Add mood phrase
        mood_phrase = self._get_mood_phrase(mood)
        parts.append(f"This read is {mood_phrase}.")
        
        # Add top factor reasons
        if top_factors:
            reasons = [f['explanation'] for f in top_factors]
            parts.append(' '.join(reasons) + '.')
        
        # Add rating if available
        rating = book.get('rating', 0)
        if rating > 0:
            parts.append(f"Rated {rating:.1f}/5 by readers.")
        
        return ' '.join(parts)
    
    def _generate_summary(self, book: Dict[str, Any], 
                         mood: str,
                         factors: List[Dict]) -> str:
        """Generate a brief summary."""
        score_pct = book.get('score_percentage', 0)
        mood_phrase = self._get_mood_phrase(mood)
        
        if score_pct >= 80:
            return f"Excellent choice! {mood_phrase.capitalize()}."
        elif score_pct >= 60:
            return f"Great match for your mood. {mood_phrase.capitalize()}."
        elif score_pct >= 40:
            return f"Good option. Offers {mood_phrase} vibes."
        else:
            return f"Worth considering for variety."
    
    def _get_mood_phrase(self, mood: str) -> str:
        """Get a descriptive phrase for the mood."""
        phrases = self.MOOD_PHRASES.get(mood, ['enjoyable', 'engaging'])
        import random
        return random.choice(phrases)
    
    def explain_comparison(self, books: List[Dict[str, Any]], 
                          mood_classification: Dict[str, Any]) -> str:
        """
        Generate explanation comparing top recommendations.
        
        Args:
            books: List of scored books
            mood_classification: Mood classification
            
        Returns:
            Comparison explanation text
        """
        if not books:
            return "No books to compare."
        
        if len(books) == 1:
            return self.explain(books[0], mood_classification)['main_explanation']
        
        primary_mood = mood_classification.get('primary_mood', 'curious')
        
        # Compare top 2-3 books
        top_books = books[:min(3, len(books))]
        
        parts = []
        parts.append(f"Based on your {primary_mood} mood, here's how your books compare:\n")
        
        for i, book in enumerate(top_books):
            title = book.get('title', 'Unknown')
            score = book.get('score_percentage', 0)
            parts.append(f"**#{i+1} {title}** ({score}% match)")
        
        # Explain why #1 is top
        top_book = top_books[0]
        top_scores = top_book.get('scores', {})
        best_factor = max(top_scores.items(), key=lambda x: x[1])[0] if top_scores else 'mood_match'
        
        factor_names = {
            'mood_match': 'mood alignment',
            'genre_preference': 'genre match',
            'reading_history': 'novelty',
            'difficulty': 'reading level',
            'popularity': 'reader ratings'
        }
        
        parts.append(f"\n{top_books[0].get('title')} leads due to its excellent {factor_names.get(best_factor, 'overall score')}.")
        
        return '\n'.join(parts)


# Singleton instance
_explainer: Optional[RecommendationExplainer] = None

def get_explainer() -> RecommendationExplainer:
    """Get or create the explainer singleton."""
    global _explainer
    if _explainer is None:
        _explainer = RecommendationExplainer()
    return _explainer
