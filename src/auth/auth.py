"""
Authentication Module - Supabase Auth
"""
import streamlit as st
from typing import Optional, Dict, Any
from src.database.supabase_client import get_client


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get currently logged in user from session."""
    return st.session_state.get('user')


def get_user_id() -> Optional[str]:
    """Get current user's ID."""
    user = get_current_user()
    return user.get('id') if user else None


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return get_current_user() is not None


def sign_up(email: str, password: str) -> Dict[str, Any]:
    """Sign up new user. Does NOT auto-login - user must confirm email first."""
    client = get_client()
    try:
        response = client.auth.sign_up({
            'email': email,
            'password': password
        })
        
        if response.user:
            # Don't auto-login - user needs to confirm email first
            return {
                'success': True, 
                'email': response.user.email,
                'message': 'Check your email to confirm your account'
            }
        else:
            return {'success': False, 'error': 'Sign up failed'}
            
    except Exception as e:
        error_msg = str(e)
        if 'already registered' in error_msg.lower():
            return {'success': False, 'error': 'This email is already registered. Try signing in instead.'}
        return {'success': False, 'error': str(e)}


def sign_in(email: str, password: str) -> Dict[str, Any]:
    """Sign in existing user."""
    client = get_client()
    try:
        response = client.auth.sign_in_with_password({
            'email': email,
            'password': password
        })
        
        if response.user:
            st.session_state['user'] = {
                'id': response.user.id,
                'email': response.user.email,
                'created_at': str(response.user.created_at)
            }
            return {'success': True, 'user': st.session_state['user']}
        else:
            return {'success': False, 'error': 'Invalid credentials'}
            
    except Exception as e:
        error_msg = str(e).lower()
        if 'invalid login' in error_msg or 'invalid' in error_msg:
            return {'success': False, 'error': 'Invalid email or password. Did you sign up first?'}
        if 'email not confirmed' in error_msg or 'confirm' in error_msg:
            return {'success': False, 'error': 'Please check your email and click the verification link first.'}
        if 'user not found' in error_msg:
            return {'success': False, 'error': 'No account found with this email. Please sign up first.'}
        return {'success': False, 'error': str(e)}


def sign_out():
    """Sign out current user."""
    client = get_client()
    try:
        client.auth.sign_out()
    except:
        pass
    
    # Clear session
    st.session_state.pop('user', None)
    # Clear other user data
    for key in ['uploaded_image', 'detected_books', 'recommendations', 'mood_classification']:
        st.session_state.pop(key, None)


def reset_password(email: str) -> Dict[str, Any]:
    """Send password reset email."""
    client = get_client()
    try:
        client.auth.reset_password_email(email)
        return {'success': True, 'message': 'Password reset email sent'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
