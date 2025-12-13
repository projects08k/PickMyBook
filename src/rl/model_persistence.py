"""
Model Persistence for Q-Learning Agent
Cloud-ready: Uses Supabase with SERVICE ROLE for persistent Q-table storage.
Uses admin client to bypass RLS for global model updates.
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime


class SupabaseModelPersistence:
    """
    Handles saving and loading of Q-learning model state to Supabase.
    Uses a single global model that learns from all users.
    Uses SERVICE ROLE key to bypass RLS for global operations.
    """
    
    def __init__(self):
        """Initialize Supabase model persistence."""
        self._supabase = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Supabase client with admin privileges."""
        try:
            from src.database.supabase_client import get_admin_client
            self._supabase = get_admin_client()
        except Exception as e:
            print(f"Supabase persistence not available: {e}")
    
    def save(self, agent) -> bool:
        """
        Save agent state to Supabase.
        
        Args:
            agent: QLearningAgent instance
            
        Returns:
            True if successful
        """
        if not self._supabase:
            return False
        
        try:
            # Prepare Q-table as JSON-serializable dict
            q_table = agent.get_q_table()
            # Convert tuple keys to strings for JSON
            q_table_json = {str(k): v for k, v in q_table.items()}
            
            stats = {
                'total_accepts': agent.total_accepts,
                'total_rejects': agent.total_rejects,
                'learning_steps': agent.learning_steps
            }
            
            # Upsert global model
            self._supabase.table('rl_model').upsert({
                'id': 'global',
                'q_table': q_table_json,
                'stats': stats,
                'epsilon': agent.epsilon,
                'learning_rate': agent.learning_rate,
                'updated_at': datetime.now().isoformat()
            }).execute()
            
            return True
            
        except Exception as e:
            print(f"Error saving model to Supabase: {e}")
            return False
    
    def load(self, agent) -> bool:
        """
        Load agent state from Supabase.
        
        Args:
            agent: QLearningAgent instance to populate
            
        Returns:
            True if successful
        """
        if not self._supabase:
            return False
        
        try:
            result = self._supabase.table('rl_model').select('*').eq('id', 'global').single().execute()
            
            if not result.data:
                return False
            
            data = result.data
            
            # Restore Q-table (convert string keys back to tuples)
            q_table_json = data.get('q_table', {})
            q_table = {}
            for k, v in q_table_json.items():
                try:
                    # Convert string tuple representation back to tuple
                    key = eval(k) if k.startswith('(') else k
                    q_table[key] = v
                except:
                    q_table[k] = v
            
            agent.set_q_table(q_table)
            
            # Restore stats
            stats = data.get('stats', {})
            agent.total_accepts = stats.get('total_accepts', 0)
            agent.total_rejects = stats.get('total_rejects', 0)
            agent.learning_steps = stats.get('learning_steps', 0)
            
            # Restore hyperparameters
            agent.epsilon = data.get('epsilon', 0.1)
            agent.learning_rate = data.get('learning_rate', 0.1)
            
            return True
            
        except Exception as e:
            print(f"Error loading model from Supabase: {e}")
            return False
    
    def exists(self) -> bool:
        """Check if a saved model exists in Supabase."""
        if not self._supabase:
            return False
        
        try:
            result = self._supabase.table('rl_model').select('id').eq('id', 'global').single().execute()
            return bool(result.data)
        except:
            return False
    
    def get_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the saved model."""
        if not self._supabase:
            return None
        
        try:
            result = self._supabase.table('rl_model').select('*').eq('id', 'global').single().execute()
            
            if not result.data:
                return None
            
            data = result.data
            stats = data.get('stats', {})
            
            return {
                'saved_at': data.get('updated_at'),
                'learning_steps': stats.get('learning_steps', 0),
                'total_feedback': stats.get('total_accepts', 0) + stats.get('total_rejects', 0),
                'states_learned': len(data.get('q_table', {})),
                'storage': 'supabase'
            }
        except:
            return None
    
    def is_available(self) -> bool:
        """Check if Supabase is available."""
        return self._supabase is not None


# Singleton instance
_persistence: Optional[SupabaseModelPersistence] = None

def get_model_persistence() -> SupabaseModelPersistence:
    """Get or create the model persistence singleton."""
    global _persistence
    if _persistence is None:
        _persistence = SupabaseModelPersistence()
    return _persistence


def save_agent(agent) -> bool:
    """Convenience function to save agent to Supabase."""
    return get_model_persistence().save(agent)


def load_agent(agent) -> bool:
    """Convenience function to load agent from Supabase."""
    return get_model_persistence().load(agent)
