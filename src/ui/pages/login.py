"""
Login Page - User Authentication
"""

import streamlit as st
from src.auth import sign_in, sign_up, is_authenticated


def render_login_page():
    """Render login/signup page."""
    
    if is_authenticated():
        st.session_state['page'] = 'home'
        st.rerun()
        return
    
    st.markdown("# 📚 PickMyBook")
    st.caption("AI-powered book recommendations")
    
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Centered form
    _, form_col, _ = st.columns([1, 2, 1])
    
    with form_col:
        with st.container(border=True):
            tab1, tab2 = st.tabs(["🔐 Sign In", "✨ Sign Up"])
            
            with tab1:
                _render_signin_form()
            
            with tab2:
                _render_signup_form()
        
        # Guest mode
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.caption("Or continue without account (data won't be saved)")
        if st.button("Continue as Guest", use_container_width=True):
            st.session_state['user'] = {'id': 'guest', 'email': 'guest', 'guest': True}
            st.session_state['page'] = 'home'
            st.rerun()


def _render_signin_form():
    """Render sign in form."""
    with st.form("signin_form"):
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        
        submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")
        
        if submitted:
            if not email or not password:
                st.error("Please fill in all fields")
            else:
                with st.spinner("Signing in..."):
                    result = sign_in(email, password)
                    if result['success']:
                        st.success("Welcome back!")
                        st.session_state['page'] = 'home'
                        st.rerun()
                    else:
                        st.error(result.get('error', 'Sign in failed'))


def _render_signup_form():
    """Render sign up form."""
    
    # Check if we just signed up and need to show confirmation message
    if st.session_state.get('signup_pending'):
        st.info("📧 **Check your email!**")
        st.markdown("""
        We've sent a verification link to your email address.
        
        1. Open the email from Supabase
        2. Click the confirmation link
        3. Come back here and **Sign In**
        """)
        if st.button("← Back to Sign In", use_container_width=True):
            st.session_state.pop('signup_pending', None)
            st.rerun()
        return
    
    with st.form("signup_form"):
        email = st.text_input("Email", placeholder="your@email.com", key="signup_email")
        password = st.text_input("Password", type="password", placeholder="Min 6 characters", key="signup_pass")
        confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="signup_confirm")
        
        submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")
        
        if submitted:
            if not email or not password or not confirm:
                st.error("Please fill in all fields")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            elif password != confirm:
                st.error("Passwords don't match")
            else:
                with st.spinner("Creating account..."):
                    result = sign_up(email, password)
                    if result['success']:
                        # Don't auto-login, show confirmation message
                        st.session_state['signup_pending'] = True
                        st.session_state.pop('user', None)  # Clear any auto-login
                        st.rerun()
                    else:
                        st.error(result.get('error', 'Sign up failed'))
