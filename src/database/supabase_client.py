"""
Supabase Client - Database connection
Supports both anon (user) and service role (admin) operations.
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


def get_supabase_client() -> Client:
    """Get Supabase client instance with anon key (for user operations)."""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_ANON_KEY in environment")
    
    return create_client(url, key)


def get_service_client() -> Client:
    """
    Get Supabase client with SERVICE ROLE key (bypasses RLS).
    Use for admin operations like global RL model updates.
    """
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not url or not key:
        # Fall back to anon key if service role not available
        return get_supabase_client()
    
    return create_client(url, key)


# Singleton instances
_client: Client = None
_service_client: Client = None


def get_client() -> Client:
    """Get singleton Supabase client (anon key)."""
    global _client
    if _client is None:
        _client = get_supabase_client()
    return _client


def get_admin_client() -> Client:
    """Get singleton Supabase client with service role (bypasses RLS)."""
    global _service_client
    if _service_client is None:
        _service_client = get_service_client()
    return _service_client

