"""
components/styles.py
CSS injection utilities for Saga.

Usage:
    from components.styles import inject_css
    inject_css()   # call once near the top of each page

Individual helpers are also importable for surgical injection:
    from components.styles import card_css, gradient_title_css, chip_css
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Base palette (mirrors .streamlit/config.toml)
# ---------------------------------------------------------------------------
COLORS = {
    "bg": "#0E0E1A",
    "card_bg": "#1A1A2E",
    "card_border": "#2E2E4E",
    "primary": "#7C5CBF",
    "primary_light": "#9B7FD4",
    "primary_dark": "#5A3F9A",
    "accent": "#C084FC",
    "text": "#E8E4F0",
    "text_muted": "#9B96B0",
    "success": "#4ADE80",
    "warning": "#FBBF24",
    "danger": "#F87171",
    "info": "#60A5FA",
}

# ---------------------------------------------------------------------------
# CSS blocks
# ---------------------------------------------------------------------------

def _base_css() -> str:
    """Reset and global styles."""
    return f"""
    /* ---- Saga base reset ---- */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {COLORS['bg']};
        color: {COLORS['text']};
    }}
    [data-testid="stSidebar"] {{
        background-color: {COLORS['card_bg']};
        border-right: 1px solid {COLORS['card_border']};
    }}
    /* Remove default Streamlit top padding */
    .block-container {{
        padding-top: 1.5rem;
    }}
    /* Scrollbar */
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: {COLORS['bg']}; }}
    ::-webkit-scrollbar-thumb {{ background: {COLORS['primary_dark']}; border-radius: 3px; }}
    """


def card_css() -> str:
    """Dark card / panel styling."""
    return f"""
    /* ---- Dark cards ---- */
    .saga-card {{
        background-color: {COLORS['card_bg']};
        border: 1px solid {COLORS['card_border']};
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }}
    .saga-card-accent {{
        background-color: {COLORS['card_bg']};
        border: 1px solid {COLORS['primary']};
        border-left: 4px solid {COLORS['primary']};
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }}
    /* Metric cards row */
    .saga-metric-card {{
        background: linear-gradient(135deg, {COLORS['card_bg']} 0%, #221d38 100%);
        border: 1px solid {COLORS['card_border']};
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }}
    .saga-metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {COLORS['primary_light']};
        line-height: 1.1;
    }}
    .saga-metric-label {{
        font-size: 0.78rem;
        color: {COLORS['text_muted']};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.25rem;
    }}
    """


def gradient_title_css() -> str:
    """Gradient headline text used on the weekly narrative and page titles."""
    return f"""
    /* ---- Gradient titles ---- */
    .saga-gradient-title {{
        background: linear-gradient(90deg, {COLORS['primary_light']} 0%, {COLORS['accent']} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 0.25rem;
    }}
    .saga-section-title {{
        color: {COLORS['primary_light']};
        font-size: 1.1rem;
        font-weight: 600;
        border-bottom: 1px solid {COLORS['card_border']};
        padding-bottom: 0.4rem;
        margin-bottom: 0.75rem;
    }}
    """


def chip_css() -> str:
    """Priority and category chip/badge styling."""
    return f"""
    /* ---- Priority / category chips ---- */
    .saga-chip {{
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 0.15rem 0.2rem;
        letter-spacing: 0.03em;
    }}
    .chip-high {{
        background-color: rgba(248, 113, 113, 0.18);
        color: {COLORS['danger']};
        border: 1px solid {COLORS['danger']};
    }}
    .chip-medium {{
        background-color: rgba(251, 191, 36, 0.18);
        color: {COLORS['warning']};
        border: 1px solid {COLORS['warning']};
    }}
    .chip-low {{
        background-color: rgba(74, 222, 128, 0.18);
        color: {COLORS['success']};
        border: 1px solid {COLORS['success']};
    }}
    .chip-work {{
        background-color: rgba(96, 165, 250, 0.18);
        color: {COLORS['info']};
        border: 1px solid {COLORS['info']};
    }}
    .chip-personal {{
        background-color: rgba(192, 132, 252, 0.18);
        color: {COLORS['accent']};
        border: 1px solid {COLORS['accent']};
    }}
    .chip-health {{
        background-color: rgba(74, 222, 128, 0.18);
        color: {COLORS['success']};
        border: 1px solid {COLORS['success']};
    }}
    .chip-creative {{
        background-color: rgba(251, 191, 36, 0.18);
        color: {COLORS['warning']};
        border: 1px solid {COLORS['warning']};
    }}
    .chip-admin {{
        background-color: rgba(156, 163, 175, 0.18);
        color: #9CA3AF;
        border: 1px solid #9CA3AF;
    }}
    """


def intention_card_css() -> str:
    """Gradient 'Daily Intention' highlight card."""
    return f"""
    /* ---- Daily Intention card ---- */
    .saga-intention {{
        background: linear-gradient(135deg, {COLORS['primary_dark']} 0%, #1e1540 100%);
        border: 1px solid {COLORS['primary']};
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin: 1rem 0;
        text-align: center;
    }}
    .saga-intention-label {{
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: {COLORS['accent']};
        font-weight: 600;
        margin-bottom: 0.5rem;
    }}
    .saga-intention-text {{
        font-size: 1.25rem;
        font-style: italic;
        color: {COLORS['text']};
        line-height: 1.5;
    }}
    """


def sidebar_css() -> str:
    """Sidebar-specific overrides: streak badge, logo, nav links."""
    return f"""
    /* ---- Sidebar ---- */
    .saga-sidebar-logo {{
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, {COLORS['primary_light']} 0%, {COLORS['accent']} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }}
    .saga-streak-badge {{
        background: linear-gradient(90deg, {COLORS['primary']} 0%, {COLORS['accent']} 100%);
        border-radius: 999px;
        padding: 0.35rem 1rem;
        font-size: 0.9rem;
        font-weight: 700;
        color: #fff;
        display: inline-block;
        margin: 0.5rem 0;
    }}
    .saga-date-display {{
        font-size: 0.82rem;
        color: {COLORS['text_muted']};
        margin-top: 0.25rem;
    }}
    """


def streaming_css() -> str:
    """Typewriter cursor effect for the Weekly Narrator streaming output."""
    return f"""
    /* ---- Streaming / typewriter ---- */
    .saga-streaming-cursor::after {{
        content: '|';
        display: inline-block;
        color: {COLORS['accent']};
        animation: saga-blink 0.9s step-end infinite;
        margin-left: 1px;
    }}
    @keyframes saga-blink {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0; }}
    }}
    .saga-narrative {{
        background-color: {COLORS['card_bg']};
        border: 1px solid {COLORS['card_border']};
        border-radius: 12px;
        padding: 1.5rem 2rem;
        line-height: 1.8;
        font-size: 1rem;
        color: {COLORS['text']};
    }}
    """


def mood_emoji_css() -> str:
    """Oversized clickable mood selector buttons."""
    return f"""
    /* ---- Mood emoji selector ---- */
    .saga-mood-row {{
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin: 0.5rem 0;
    }}
    .saga-mood-btn {{
        background: {COLORS['card_bg']};
        border: 2px solid {COLORS['card_border']};
        border-radius: 10px;
        padding: 0.4rem 0.75rem;
        font-size: 1.4rem;
        cursor: pointer;
        transition: border-color 0.15s, transform 0.1s;
    }}
    .saga-mood-btn:hover {{
        border-color: {COLORS['primary']};
        transform: scale(1.1);
    }}
    .saga-mood-btn.selected {{
        border-color: {COLORS['accent']};
        background: rgba(124, 92, 191, 0.25);
    }}
    """


# ---------------------------------------------------------------------------
# Master inject function
# ---------------------------------------------------------------------------

def inject_css() -> None:
    """
    Inject all Saga CSS into the current Streamlit page.
    Call once near the top of every page script.
    """
    css = "".join([
        _base_css(),
        card_css(),
        gradient_title_css(),
        chip_css(),
        intention_card_css(),
        sidebar_css(),
        streaming_css(),
        mood_emoji_css(),
    ])
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Convenience HTML builders
# ---------------------------------------------------------------------------

def render_chip(label: str, chip_class: str = "chip-work") -> str:
    """Return an HTML string for a single chip. Use with st.markdown(..., unsafe_allow_html=True)."""
    return f'<span class="saga-chip {chip_class}">{label}</span>'


def render_priority_chip(priority: str) -> str:
    """Map 'high'/'medium'/'low' to the correct chip HTML."""
    mapping = {"high": "chip-high", "medium": "chip-medium", "low": "chip-low"}
    css_class = mapping.get(str(priority).lower(), "chip-low")
    return render_chip(priority.capitalize(), css_class)


def render_category_chip(category: str) -> str:
    """Map a task category string to the correct chip HTML."""
    css_class = f"chip-{str(category).lower()}"
    return render_chip(category.capitalize(), css_class)


def render_intention_card(intention_text: str) -> str:
    """Return the HTML for the gradient Daily Intention card."""
    return (
        '<div class="saga-intention">'
        '<div class="saga-intention-label">Daily Intention</div>'
        f'<div class="saga-intention-text">{intention_text}</div>'
        "</div>"
    )


def render_metric_card(value: str, label: str) -> str:
    """Return the HTML for a single metric card."""
    return (
        '<div class="saga-metric-card">'
        f'<div class="saga-metric-value">{value}</div>'
        f'<div class="saga-metric-label">{label}</div>'
        "</div>"
    )


def render_gradient_title(text: str) -> str:
    """Return the HTML for a gradient page/section title."""
    return f'<h1 class="saga-gradient-title">{text}</h1>'
