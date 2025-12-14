"""
PickMyBook - AI Book Recommendation System
With Multi-User Authentication
"""

import streamlit as st
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from src.ui.styles import apply_theme
from src.ui.pages import (
    render_home_page,
    render_results_page,
    render_recommendation_page,
    render_history_page,
    render_settings_page,
    render_login_page
)
from src.auth import is_authenticated, sign_out, get_current_user


st.set_page_config(
    page_title="PickMyBook",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)


def main():
    """Main app entry point."""
    
    apply_theme()
    
    # Initialize page
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'
    
    # Check if Supabase is configured
    supabase_configured = os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_ANON_KEY')
    
    # If not authenticated and Supabase is configured, show login
    if supabase_configured and not is_authenticated() and st.session_state['page'] != 'login':
        st.session_state['page'] = 'login'
    
    # Sidebar with user info
    with st.sidebar:
        st.markdown("""
        <div style="padding: 0.75rem 0; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.06);">
            <h3 style="margin: 0; font-family: 'Crimson Pro', serif; color: #fafafa;">📚 PickMyBook</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Show user info if authenticated
        if is_authenticated():
            user = get_current_user()
            email = user.get('email', 'Guest')
            is_guest = user.get('guest', False)
            
            st.markdown(f"<div style='padding: 0.5rem 0; font-size: 0.75rem; color: #888;'>👤 {email}</div>", unsafe_allow_html=True)
            
            if not is_guest:
                if st.button("🚪 Sign Out", use_container_width=True):
                    sign_out()
                    st.session_state['page'] = 'login'
                    st.rerun()
        
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        
        # Navigation
        pages = [
            ("🏠 Home", "home"),
            ("📚 Results", "results"),
            ("✨ Recommend", "recommendation"),
            ("📜 History", "history"),
            ("⚙️ Settings", "settings"),
        ]
        
        for label, key in pages:
            if not is_authenticated() and key != 'login':
                continue
            current = st.session_state['page'] == key
            if st.button(label, key=f"nav_{key}", use_container_width=True, 
                        type="primary" if current else "secondary"):
                st.session_state['page'] = key
                st.rerun()
    
    # Route to page
    page = st.session_state.get('page', 'login')
    
    # If not authenticated, force login page
    if supabase_configured and not is_authenticated():
        render_login_page()
        return
    
    routes = {
        'login': render_login_page,
        'home': render_home_page,
        'results': render_results_page,
        'recommendation': render_recommendation_page,
        'history': render_history_page,
        'settings': render_settings_page,
    }
    
    routes.get(page, render_home_page)()


if __name__ == "__main__":
    main()
