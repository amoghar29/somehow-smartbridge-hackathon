"""
Custom card components for the UI.
"""

import streamlit as st


def metric_card(title: str, value: str, delta: str = None, color: str = "blue"):
    """Create a custom metric card"""
    colors = {
        "blue": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "green": "linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)",
        "red": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "yellow": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"
    }

    background = colors.get(color, colors["blue"])

    html = f"""
    <div style="
        background: {background};
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <h4 style="margin:0;">{title}</h4>
        <h2 style="margin:0.5rem 0;">{value}</h2>
        {f'<p style="margin:0;opacity:0.8;">{delta}</p>' if delta else ''}
    </div>
    """

    return st.markdown(html, unsafe_allow_html=True)


def summary_card(title: str, items: list):
    """Create a summary card with list items"""
    items_html = "".join([f"<li>{item}</li>" for item in items])

    html = f"""
    <div style="
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    ">
        <h4 style="margin:0 0 1rem 0;">{title}</h4>
        <ul style="margin:0;padding-left:1.5rem;">
            {items_html}
        </ul>
    </div>
    """

    return st.markdown(html, unsafe_allow_html=True)
