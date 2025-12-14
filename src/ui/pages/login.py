"""
Login Page - User Authentication
"""

import streamlit as st
from urllib.parse import urlparse, parse_qs
from src.auth import sign_in, sign_up, is_authenticated, sign_in_with_oauth, handle_oauth_callback

# Get the app URL for OAuth redirects
def get_app_url():
    """Get the current app URL for OAuth redirect."""
    # For Streamlit Cloud, use the public URL
    # This will be set automatically in production
    import os
    # Check if running on Streamlit Cloud
    if os.getenv('STREAMLIT_RUNTIME_ENV') == 'cloud':
        # You'll need to set this in your secrets
        return os.getenv('APP_URL', 'https://your-app.streamlit.app')
    return 'http://localhost:8501'


def handle_oauth_tokens():
    """Check URL for OAuth callback tokens and handle them."""
    # Get query params from URL fragment (hash)
    # Supabase sends tokens in the URL fragment after OAuth
    try:
        # Check if we have tokens in session from JavaScript redirect
        if 'oauth_tokens' in st.session_state:
            tokens = st.session_state.pop('oauth_tokens')
            result = handle_oauth_callback(
                tokens.get('access_token'),
                tokens.get('refresh_token')
            )
            if result['success']:
                st.session_state['page'] = 'home'
                st.rerun()
    except Exception as e:
        st.error(f"OAuth error: {e}")


def render_login_page():
    """Render login/signup page."""
    
    # Handle OAuth callback if present
    handle_oauth_tokens()
    
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
        
        # OAuth buttons
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("<center>— or continue with —</center>", unsafe_allow_html=True)
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔵 Google", use_container_width=True):
                _handle_oauth_login('google')
        
        with col2:
            if st.button("⚫ GitHub", use_container_width=True):
                _handle_oauth_login('github')
        
        # Guest mode
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.caption("Or continue without account (data won't be saved)")
        if st.button("Continue as Guest", use_container_width=True):
            st.session_state['user'] = {'id': 'guest', 'email': 'guest', 'guest': True}
            st.session_state['page'] = 'home'
            st.rerun()


def _handle_oauth_login(provider: str):
    """Handle OAuth login redirect."""
    app_url = get_app_url()
    result = sign_in_with_oauth(provider, app_url)
    
    if result['success'] and result.get('url'):
        oauth_url = result['url']
        # Use JavaScript to redirect in new tab or parent window (avoids iframe issues)
        st.markdown(f'''
            <script>
                // Try to redirect the parent window (if in iframe)
                if (window.top !== window.self) {{
                    window.top.location.href = "{oauth_url}";
                }} else {{
                    window.location.href = "{oauth_url}";
                }}
            </script>
            <noscript>
                <meta http-equiv="refresh" content="0; url={oauth_url}">
            </noscript>
        ''', unsafe_allow_html=True)
        
        # Also show a clickable link as fallback
        st.info(f"Redirecting to {provider.title()}...")
        st.markdown(f"If not redirected, [click here to login with {provider.title()}]({oauth_url})")
    else:
        st.error(f"Failed to connect to {provider.title()}: {result.get('error', 'Unknown error')}")


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
