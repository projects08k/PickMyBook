"""
Home Page - Clean Design
"""

import streamlit as st
from PIL import Image


MOODS = [
    ("Relaxed", "Wind down with something calming"),
    ("Adventurous", "Explore new worlds and ideas"),
    ("Romantic", "Stories of love and connection"),
    ("Thoughtful", "Deep, philosophical reads"),
    ("Excited", "Fast-paced and thrilling"),
    ("Melancholic", "Bittersweet and moving"),
    ("Curious", "Learn something new"),
    ("Escapist", "Fantasy and imagination"),
]


def render_home_page():
    """Render clean home page."""
    
    # Header
    st.markdown("# 📚 PickMyBook")
    st.caption("AI-powered book recommendations tailored to your mood")
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    # Two columns
    col1, col2 = st.columns(2, gap="medium")
    
    # STEP 1: Upload
    with col1:
        with st.container(border=True):
            st.caption("STEP 1")
            st.markdown("**Upload Your Bookshelf**")
            
            if st.session_state.get('uploaded_image'):
                # Show image with remove button
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.image(st.session_state['uploaded_image'], width=160)
                with c2:
                    if st.button("✕", key="rm", help="Remove"):
                        st.session_state.pop('uploaded_image', None)
                        st.session_state.pop('image_name', None)
                        st.rerun()
                st.success("✓ Ready")
            else:
                st.caption("Take a photo of your books")
                uploaded = st.file_uploader(
                    "bookshelf",
                    type=['png', 'jpg', 'jpeg', 'webp'],
                    label_visibility="collapsed"
                )
                if uploaded:
                    uploaded.seek(0)
                    st.session_state['uploaded_image'] = uploaded.read()
                    st.session_state['image_name'] = uploaded.name
                    st.rerun()
    
    # STEP 2: Mood
    with col2:
        with st.container(border=True):
            st.caption("STEP 2")
            st.markdown("**How Are You Feeling?**")
            
            mood_opts = ["Choose your mood..."] + [m[0] for m in MOODS]
            selected = st.selectbox("Mood", options=mood_opts, index=0, label_visibility="collapsed")
            
            if selected != "Choose your mood...":
                st.session_state['selected_mood'] = selected.lower()
                desc = next((m[1] for m in MOODS if m[0] == selected), "")
                st.session_state['mood_text'] = f"I'm feeling {selected.lower()}. {desc}"
                st.caption(f"💭 {desc}")
            
            extra = st.text_area("Details", placeholder="Anything specific? (optional)", height=60, label_visibility="collapsed")
            if extra:
                cur = st.session_state.get('mood_text', '')
                st.session_state['mood_text'] = f"{cur} {extra}".strip()
    
    # Action button
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    can_go = st.session_state.get('uploaded_image') and st.session_state.get('selected_mood')
    
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("Pick My Next Read →" if can_go else "Complete both steps", use_container_width=True, disabled=not can_go):
            st.session_state['page'] = 'results'
            st.session_state['analyzing'] = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # History button
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
    _, hist_col, _ = st.columns([1, 1, 1])
    with hist_col:
        if st.button("📜 View Reading History", use_container_width=True):
            st.session_state['page'] = 'history'
            st.rerun()
    
    # Features
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    f1, f2, f3 = st.columns(3, gap="small")
    with f1:
        with st.container(border=True):
            st.markdown("📷 **Vision AI**")
            st.caption("Detects books from photos")
    with f2:
        with st.container(border=True):
            st.markdown("🎯 **Mood Match**")
            st.caption("Tailored to how you feel")
    with f3:
        with st.container(border=True):
            st.markdown("🧠 **Learns**")
            st.caption("Improves with feedback")
