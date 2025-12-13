"""
Q-Learning Agent for Adaptive Book Recommendations
Learns from user feedback to improve recommendations over time.
"""

import random
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict


class QLearningAgent:
    """
    Q-Learning agent that improves book recommendations based on user feedback.
    
    State: (mood_category, genre) tuple
    Action: recommend book from specific genre
    Reward: +1 for accept, -1 for reject
    """
    
    def __init__(self, 
                 learning_rate: float = 0.1,
                 discount_factor: float = 0.9,
                 epsilon: float = 0.1):
        """
        Initialize the Q-Learning agent.
        
        Args:
            learning_rate: Alpha - how much new information overrides old
            discount_factor: Gamma - importance of future rewards
            epsilon: Probability of exploration vs exploitation
        """
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        
        # Q-table: maps (state, action) -> value
        # state = (mood, user_genre_preference_hash)
        # action = genre to recommend
        self.q_table: Dict[Tuple[str, str], Dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )
        
        # Track statistics
        self.total_accepts = 0
        self.total_rejects = 0
        self.learning_steps = 0
        
        # All possible genres (actions)
        self.all_genres = [
            'Fiction', 'Non-fiction', 'Mystery', 'Thriller', 'Romance',
            'Fantasy', 'Science Fiction', 'Horror', 'Adventure', 'Drama',
            'Biography', 'History', 'Philosophy', 'Psychology', 'Self-help',
            'Poetry', 'Humor', 'Literary Fiction', 'Contemporary Fiction',
            'Historical Fiction', 'Cozy Mystery', 'True Crime'
        ]
    
    def get_state(self, mood: str, user_preferences: Optional[Dict] = None) -> str:
        """
        Create a state representation from mood and preferences.
        
        Args:
            mood: Primary mood category
            user_preferences: Optional user preference dict
            
        Returns:
            State string
        """
        # Simple state: just the mood
        # Could be extended to include more context
        return mood.lower() if mood else 'unknown'
    
    def select_action(self, state: str, available_genres: List[str]) -> str:
        """
        Select a genre to recommend using epsilon-greedy policy.
        
        Args:
            state: Current state
            available_genres: List of genres available in detected books
            
        Returns:
            Selected genre
        """
        if not available_genres:
            return random.choice(self.all_genres)
        
        # Epsilon-greedy: explore with probability epsilon
        if random.random() < self.epsilon:
            return random.choice(available_genres)
        
        # Exploit: choose best action based on Q-values
        state_q_values = self.q_table[state]
        
        # Filter to available genres
        available_q = {
            genre: state_q_values.get(genre, 0.0) 
            for genre in available_genres
        }
        
        if not available_q:
            return random.choice(available_genres)
        
        # Return genre with highest Q-value
        return max(available_q.items(), key=lambda x: x[1])[0]
    
    def get_genre_scores(self, state: str) -> Dict[str, float]:
        """
        Get Q-values for all genres in a state.
        
        Args:
            state: Current state
            
        Returns:
            Dictionary of genre -> Q-value
        """
        return dict(self.q_table[state])
    
    def update(self, state: str, action: str, reward: float, 
               next_state: Optional[str] = None):
        """
        Update Q-value based on feedback.
        
        Args:
            state: State when action was taken
            action: Genre that was recommended
            reward: +1 for accept, -1 for reject
            next_state: Next state (optional, usually same as state)
        """
        next_state = next_state or state
        
        # Get current Q-value
        current_q = self.q_table[state][action]
        
        # Get max Q-value for next state
        next_q_values = self.q_table[next_state]
        max_next_q = max(next_q_values.values()) if next_q_values else 0.0
        
        # Q-learning update formula
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state][action] = new_q
        self.learning_steps += 1
        
        # Update statistics
        if reward > 0:
            self.total_accepts += 1
        else:
            self.total_rejects += 1
    
    def record_feedback(self, mood: str, genre: str, accepted: bool):
        """
        Convenience method to record user feedback.
        
        Args:
            mood: User's mood when recommendation was made
            genre: Genre of the recommended book
            accepted: True if user accepted, False if rejected
        """
        state = self.get_state(mood)
        reward = 1.0 if accepted else -1.0
        self.update(state, genre, reward)
    
    def adjust_book_scores(self, books: List[Dict[str, Any]], 
                          mood: str) -> List[Dict[str, Any]]:
        """
        Adjust book scores based on learned preferences.
        
        Args:
            books: List of scored books
            mood: Current mood
            
        Returns:
            Books with adjusted scores
        """
        state = self.get_state(mood)
        q_values = self.get_genre_scores(state)
        
        if not q_values:
            return books  # No learning yet
        
        # Normalize Q-values to 0-1 range for blending
        min_q = min(q_values.values()) if q_values else 0
        max_q = max(q_values.values()) if q_values else 0
        q_range = max_q - min_q if max_q != min_q else 1
        
        adjusted_books = []
        for book in books:
            adjusted = book.copy()
            
            # Get book's genre
            genre = book.get('genre', 'Fiction')
            if isinstance(genre, list):
                genre = genre[0] if genre else 'Fiction'
            
            # Find matching Q-value
            q_bonus = 0.0
            for q_genre, q_val in q_values.items():
                if q_genre.lower() in genre.lower() or genre.lower() in q_genre.lower():
                    # Normalize to 0-0.1 bonus range
                    normalized_q = (q_val - min_q) / q_range if q_range else 0
                    q_bonus = normalized_q * 0.1
                    break
            
            # Adjust total score
            original_score = adjusted.get('total_score', 0)
            adjusted['total_score'] = min(original_score + q_bonus, 1.0)
            adjusted['score_percentage'] = round(adjusted['total_score'] * 100, 1)
            adjusted['rl_bonus'] = round(q_bonus, 3)
            
            adjusted_books.append(adjusted)
        
        # Re-sort by adjusted score
        adjusted_books.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Update ranks
        for i, book in enumerate(adjusted_books):
            book['rank'] = i + 1
        
        return adjusted_books
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get learning statistics."""
        total = self.total_accepts + self.total_rejects
        acceptance_rate = self.total_accepts / total if total > 0 else 0
        
        return {
            'total_accepts': self.total_accepts,
            'total_rejects': self.total_rejects,
            'total_feedback': total,
            'acceptance_rate': round(acceptance_rate, 2),
            'learning_steps': self.learning_steps,
            'states_learned': len(self.q_table),
            'epsilon': self.epsilon,
            'learning_rate': self.learning_rate
        }
    
    def decay_epsilon(self, decay_rate: float = 0.99, min_epsilon: float = 0.01):
        """
        Decay epsilon to reduce exploration over time.
        
        Args:
            decay_rate: Multiplicative decay factor
            min_epsilon: Minimum epsilon value
        """
        self.epsilon = max(self.epsilon * decay_rate, min_epsilon)
    
    def get_q_table(self) -> Dict:
        """Get the Q-table for persistence."""
        # Convert defaultdict to regular dict for pickling
        return {
            state: dict(actions) 
            for state, actions in self.q_table.items()
        }
    
    def set_q_table(self, q_table: Dict):
        """Set the Q-table from loaded data."""
        self.q_table = defaultdict(lambda: defaultdict(float))
        for state, actions in q_table.items():
            for action, value in actions.items():
                self.q_table[state][action] = value


# Singleton instance
_agent: Optional[QLearningAgent] = None

def get_q_learning_agent() -> QLearningAgent:
    """Get or create the Q-Learning agent singleton."""
    global _agent
    if _agent is None:
        _agent = QLearningAgent()
    return _agent
