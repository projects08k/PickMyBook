"""
UI Module
"""
from .styles import apply_theme, render_score_ring, render_progress_bar, render_tags
from .pages import (
    render_home_page,
    render_results_page,
    render_recommendation_page,
    render_history_page,
    render_settings_page
)

__all__ = [
    'apply_theme',
    'render_score_ring',
    'render_progress_bar',
    'render_tags',
    'render_home_page',
    'render_results_page',
    'render_recommendation_page',
    'render_history_page',
    'render_settings_page'
]
