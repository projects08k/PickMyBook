"""
Login Page - User Authentication
"""

import streamlit as st
from urllib.parse import urlparse, parse_qs
from src.auth import sign_in, sign_up, is_authenticated, sign_in_with_oauth, handle_oauth_callback

# Get the app URL for OAuth redirects
def get_app_url():
    """Get the current app URL for OAuth redirect."""
    import os
    
    # Try to get from Streamlit secrets first (for Streamlit Cloud)
    try:
        if hasattr(st, 'secrets') and 'APP_URL' in st.secrets:
            return st.secrets['APP_URL']
    except:
        pass
    
    # Fallback to environment variable
    app_url = os.getenv('APP_URL')
    if app_url:
        return app_url
    
    # Default for local development
    return 'http://localhost:8501'


def handle_oauth_callback_from_url():
    """
    Handle OAuth callback by extracting tokens from URL.
    Supabase OAuth returns tokens in URL hash, which we need to capture via JavaScript.
    """
    # Check for access_token in query params (set by our JavaScript handler)
    query_params = st.query_params
    
    if 'access_token' in query_params:
        access_token = query_params.get('access_token')
        refresh_token = query_params.get('refresh_token', '')
        
        if access_token:
            try:
                from src.auth import handle_oauth_callback
                result = handle_oauth_callback(access_token, refresh_token)
                
                if result['success']:
                    # Clear the tokens from URL
                    st.query_params.clear()
                    st.session_state['page'] = 'home'
                    st.rerun()
                else:
                    st.error(f"Login failed: {result.get('error', 'Unknown error')}")
                    st.query_params.clear()
            except Exception as e:
                st.error(f"OAuth error: {e}")
                st.query_params.clear()
        return  # Don't add JS if we already have query params
    
    # Only add JavaScript if we don't already have a session and no query params
    # This script extracts tokens from URL hash and redirects with query params
    if not st.session_state.get('oauth_js_added'):
        st.session_state['oauth_js_added'] = True
        st.components.v1.html('''
            <script>
                (function() {
                    const hash = window.location.hash;
                    if (hash && hash.includes('access_token=')) {
                        const params = new URLSearchParams(hash.substring(1));
                        const accessToken = params.get('access_token');
                        const refreshToken = params.get('refresh_token');
                        
                        if (accessToken) {
                            const baseUrl = window.location.origin + window.location.pathname;
                            const newUrl = baseUrl + '?access_token=' + encodeURIComponent(accessToken) + 
                                           '&refresh_token=' + encodeURIComponent(refreshToken || '');
                            window.location.replace(newUrl);
                        }
                    }
                })();
            </script>
        ''', height=0)


def render_login_page():
    """Render login/signup page."""
    
    # Handle OAuth callback if present
    handle_oauth_callback_from_url()
    
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
        
        # OAuth buttons - Generate URLs and show as link buttons
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("<center>— or continue with —</center>", unsafe_allow_html=True)
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        
        # Generate OAuth URLs
        app_url = get_app_url()
        google_result = sign_in_with_oauth('google', app_url)
        github_result = sign_in_with_oauth('github', app_url)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if google_result['success'] and google_result.get('url'):
                st.link_button("🔵 Google", google_result['url'], use_container_width=True)
            else:
                st.button("🔵 Google (unavailable)", use_container_width=True, disabled=True)
        
        with col2:
            if github_result['success'] and github_result.get('url'):
                st.link_button("⚫ GitHub", github_result['url'], use_container_width=True)
            else:
                st.button("⚫ GitHub (unavailable)", use_container_width=True, disabled=True)
        
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
