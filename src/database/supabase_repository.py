"""
Supabase Repository - Cloud Database Operations
Per-user data storage using Supabase
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from src.database.supabase_client import get_client
from src.auth import get_user_id


class SupabaseRepository:
    """Repository for Supabase cloud database operations."""
    
    def __init__(self):
        self.client = get_client()
    
    def _get_user_id(self) -> str:
        """Get current user ID or 'guest'."""
        return get_user_id() or 'guest'
    
    # ============ Reading History ============
    
    def add_to_history(self, title: str, author: str = None, genre: str = None,
                       mood: str = None, score: float = None, metadata: dict = None):
        """Add book to reading history."""
        user_id = self._get_user_id()
        if user_id == 'guest':
            return  # Don't save for guests
        
        self.client.table('reading_history').insert({
            'user_id': user_id,
            'title': title,
            'author': author,
            'genre': genre,
            'mood': mood,
            'score': score,
            'metadata': metadata or {}
        }).execute()
    
    def get_reading_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get reading history for current user."""
        user_id = self._get_user_id()
        if user_id == 'guest':
            return []
        
        result = self.client.table('reading_history')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        return result.data or []
    
    def get_history_titles(self) -> List[str]:
        """Get list of book titles in history."""
        history = self.get_reading_history()
        return [h.get('title') for h in history if h.get('title')]
    
    def clear_reading_history(self):
        """Clear reading history for current user."""
        user_id = self._get_user_id()
        if user_id == 'guest':
            return
        
        self.client.table('reading_history')\
            .delete()\
            .eq('user_id', user_id)\
            .execute()
    
    # ============ Feedback ============
    
    def add_feedback(self, book_title: str, genre: str = None, mood: str = None,
                     accepted: bool = False, score: float = None):
        """Record feedback for a book recommendation."""
        user_id = self._get_user_id()
        if user_id == 'guest':
            return
        
        self.client.table('feedback').insert({
            'user_id': user_id,
            'book_title': book_title,
            'genre': genre,
            'mood': mood,
            'accepted': accepted,
            'score': score
        }).execute()
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get feedback statistics for current user."""
        user_id = self._get_user_id()
        if user_id == 'guest':
            return {'total': 0, 'accepts': 0, 'acceptance_rate': 0}
        
        result = self.client.table('feedback')\
            .select('accepted')\
            .eq('user_id', user_id)\
            .execute()
        
        data = result.data or []
        total = len(data)
        accepts = sum(1 for d in data if d.get('accepted'))
        
        return {
            'total': total,
            'accepts': accepts,
            'acceptance_rate': accepts / total if total > 0 else 0
        }
    
    def get_genre_preferences(self) -> Dict[str, Dict[str, int]]:
        """Get genre preference statistics."""
        user_id = self._get_user_id()
        if user_id == 'guest':
            return {}
        
        result = self.client.table('feedback')\
            .select('genre, accepted')\
            .eq('user_id', user_id)\
            .execute()
        
        stats = {}
        for row in result.data or []:
            genre = row.get('genre', 'Unknown')
            if genre not in stats:
                stats[genre] = {'accepted': 0, 'total': 0}
            stats[genre]['total'] += 1
            if row.get('accepted'):
                stats[genre]['accepted'] += 1
        
        return stats
    
    # ============ Preferences ============
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference."""
        user_id = self._get_user_id()
        if user_id == 'guest':
            return default
        
        result = self.client.table('user_preferences')\
            .select('preferences')\
            .eq('user_id', user_id)\
            .execute()
        
        if result.data:
            prefs = result.data[0].get('preferences', {})
            return prefs.get(key, default)
        return default
    
    def set_preference(self, key: str, value: Any):
        """Set a user preference."""
        user_id = self._get_user_id()
        if user_id == 'guest':
            return
        
        # Get existing preferences
        result = self.client.table('user_preferences')\
            .select('preferences')\
            .eq('user_id', user_id)\
            .execute()
        
        if result.data:
            prefs = result.data[0].get('preferences', {})
            prefs[key] = value
            self.client.table('user_preferences')\
                .update({'preferences': prefs})\
                .eq('user_id', user_id)\
                .execute()
        else:
            self.client.table('user_preferences').insert({
                'user_id': user_id,
                'preferences': {key: value}
            }).execute()


# Singleton
_supabase_repo: SupabaseRepository = None


def get_supabase_repository() -> SupabaseRepository:
    """Get Supabase repository singleton."""
    global _supabase_repo
    if _supabase_repo is None:
        _supabase_repo = SupabaseRepository()
    return _supabase_repo
