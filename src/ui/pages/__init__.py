"""
UI Pages module initialization.
"""
from .home import render_home_page
from .results import render_results_page
from .recommendation import render_recommendation_page
from .history import render_history_page
from .settings import render_settings_page
from .login import render_login_page

__all__ = [
    'render_home_page',
    'render_results_page',
    'render_recommendation_page',
    'render_history_page',
    'render_settings_page',
    'render_login_page'
]
