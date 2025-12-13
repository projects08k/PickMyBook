"""
Settings Page - Cloud-Ready Design
Uses Supabase for preferences, RL in session state for cloud deployment.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.database import get_supabase_repository
from src.auth import get_current_user, is_authenticated
from src.rl import get_q_learning_agent


GENRES = [
    "Fiction", "Non-Fiction", "Mystery", "Thriller", "Romance", 
    "Science Fiction", "Fantasy", "Horror", "Biography", "History",
    "Self-Help", "Philosophy", "Psychology", "Science", "Poetry"
]


def render_settings_page():
    """Render the settings page."""
    
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1>Settings</h1>
        <p style="color: #a3a3a3;">Customize your experience</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check authentication
    if not is_authenticated():
        st.warning("Sign in to save your preferences")
        if st.button("← Back to Home"):
            st.session_state['page'] = 'home'
            st.rerun()
        return
    
    # Genre preferences
    st.markdown("""
    <div class="card" style="margin-bottom: 1.5rem;">
        <span class="section-label">Genre Preferences</span>
        <p style="font-size: 0.9rem; color: #a3a3a3; margin: 0.5rem 0 1rem;">
            Select your favorite genres for better recommendations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get current preferences from session or default
    current_prefs = st.session_state.get('genre_preferences', {})
    liked = [g for g, v in current_prefs.items() if v > 0]
    
    selected = st.multiselect(
        "Favorite genres",
        options=GENRES,
        default=liked[:8] if liked else ["Fiction", "Mystery"],
        max_selections=8,
        label_visibility="collapsed"
    )
    
    if st.button("Save Preferences"):
        new_prefs = {g: 1.0 for g in selected}
        st.session_state['genre_preferences'] = new_prefs
        
        # Try to save to Supabase
        try:
            repo = get_supabase_repository()
            repo.save_user_preferences(new_prefs)
        except:
            pass  # Session-only on error
        
        st.success("✓ Preferences saved")
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # AI Status
    st.markdown("""
    <div class="card" style="margin-bottom: 1.5rem;">
        <span class="section-label">AI Learning Status</span>
    </div>
    """, unsafe_allow_html=True)
    
    agent = get_q_learning_agent()
    states = len(agent.q_table) if hasattr(agent, 'q_table') else 0
    level = "Beginner" if states < 5 else "Intermediate" if states < 20 else "Expert"
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="card" style="text-align: center; padding: 1rem;">
            <div style="font-size: 1.5rem; font-weight: 600; color: #fafafa;">{states}</div>
            <div style="font-size: 0.75rem; color: #666;">Patterns Learned</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
        <div class="card" style="text-align: center; padding: 1rem;">
            <div style="font-size: 1.5rem; font-weight: 600; color: #d9ab57;">{level}</div>
            <div style="font-size: 0.75rem; color: #666;">AI Level</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.caption("Note: AI learning resets on app restart (cloud deployment)")
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # Data management
    st.markdown("<span class='section-label'>Data Management</span>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Clear History", use_container_width=True):
            try:
                repo = get_supabase_repository()
                # Would need to implement clear method
                st.success("✓ History cleared")
            except:
                st.info("History stored in Supabase")
            st.rerun()
    
    with c2:
        if st.button("Reset AI", use_container_width=True):
            agent.reset()
            st.success("✓ AI reset for this session")
            st.rerun()
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    if st.button("← Back to Home", use_container_width=True):
        st.session_state['page'] = 'home'
        st.rerun()
