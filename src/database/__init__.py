"""
Database module initialization.
Supabase-only for cloud deployment.
"""
from .supabase_client import get_client, get_admin_client
from .supabase_repository import SupabaseRepository, get_supabase_repository

__all__ = [
    'get_client',
    'get_admin_client',
    'SupabaseRepository',
    'get_supabase_repository'
]
