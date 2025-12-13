"""
History Page - Per-User Data from Supabase
"""

import streamlit as st
import os
from datetime import datetime

from src.auth import is_authenticated, get_current_user
from src.database import get_supabase_repository
from src.ui.styles import render_progress_bar, normalize_author, normalize_genre


def render_history_page():
    """Render history page with per-user data from Supabase."""
    
    st.markdown("# Reading History")
    
    user = get_current_user()
    if user and user.get('guest'):
        st.warning("You're using guest mode. History won't be saved. Sign in to save your reading history!")
        st.caption("Your book journey so far")
        _render_empty_state()
        return
    
    st.caption("Your book journey so far")
    
    # Use Supabase repository for per-user data
    try:
        repo = get_supabase_repository()
    except Exception as e:
        st.error(f"Could not connect to database: {e}")
        return
    
    # Stats from Supabase
    try:
        stats = repo.get_feedback_stats()
        total = stats.get('total', 0)
        accepted = stats.get('accepts', 0)
        rate = stats.get('acceptance_rate', 0) * 100
    except:
        total, accepted, rate = 0, 0, 0
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Books Read", accepted)
    with c2:
        st.metric("Accept Rate", f"{rate:.0f}%")
    with c3:
        st.metric("Total Rated", total)
    
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2 = st.tabs(["📚 Books", "📊 Insights"])
    
    with tab1:
        try:
            history = repo.get_reading_history(limit=15)
        except Exception as e:
            st.error(f"Error loading history: {e}")
            history = []
        
        if not history:
            st.info("No books yet. Accept some recommendations to build your list!")
        else:
            for entry in history:
                with st.container(border=True):
                    c1, c2 = st.columns([5, 1])
                    with c1:
                        title = entry.get('title', 'Unknown')
                        author = normalize_author(entry.get('author', 'Unknown'))
                        st.markdown(f"**{title}**")
                        st.caption(f"by {author}")
                    with c2:
                        ts = entry.get('created_at', entry.get('timestamp', ''))
                        if ts:
                            try:
                                dt = datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
                                st.caption(dt.strftime("%b %d"))
                            except:
                                pass
    
    with tab2:
        try:
            genre_stats = repo.get_genre_preferences()
        except:
            genre_stats = {}
        
        if not genre_stats:
            st.info("Not enough data for insights yet. Rate more recommendations!")
        else:
            st.caption("GENRE PREFERENCES")
            
            # Group by normalized genre name
            normalized_stats = {}
            for genre, s in genre_stats.items():
                clean_genre = normalize_genre(genre)
                if clean_genre not in normalized_stats:
                    normalized_stats[clean_genre] = {'accepted': 0, 'total': 0}
                normalized_stats[clean_genre]['accepted'] += s.get('accepted', 0)
                normalized_stats[clean_genre]['total'] += s.get('total', 0)
            
            sorted_genres = sorted(normalized_stats.items(), key=lambda x: x[1].get('accepted', 0), reverse=True)[:6]
            
            for genre, s in sorted_genres:
                a = s.get('accepted', 0)
                t = s.get('total', 0)
                r = (a / t * 100) if t > 0 else 0
                
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.caption(genre)
                with c2:
                    st.caption(f"{a}/{t}")
                render_progress_bar(r, 100)
    
    # Back
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        if st.button("← Back to Home", use_container_width=True):
            st.session_state['page'] = 'home'
            st.rerun()


def _render_empty_state():
    """Render empty state for guests."""
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Books Read", 0)
    with c2:
        st.metric("Accept Rate", "0%")
    with c3:
        st.metric("Total Rated", 0)
    
    st.info("Sign in to start tracking your reading history!")
    
    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        if st.button("← Back to Home", use_container_width=True, key="back_guest"):
            st.session_state['page'] = 'home'
            st.rerun()

