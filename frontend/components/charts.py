"""
Chart components for data visualization.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def create_spending_chart(data: pd.DataFrame, chart_type: str = "line"):
    """Create spending trend chart"""
    if chart_type == "line":
        fig = go.Figure()
        for column in data.columns[1:]:
            fig.add_trace(go.Scatter(
                x=data['Date'],
                y=data[column],
                mode='lines+markers',
                name=column
            ))
    elif chart_type == "bar":
        fig = go.Figure(data=[
            go.Bar(x=data['Category'], y=data['Amount'])
        ])

    fig.update_layout(
        height=400,
        hovermode='x unified',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.02)'
    )

    return fig


def create_portfolio_pie(portfolio_data: dict):
    """Create portfolio allocation pie chart"""
    fig = go.Figure(data=[go.Pie(
        labels=list(portfolio_data.keys()),
        values=list(portfolio_data.values()),
        hole=0.3
    )])

    fig.update_layout(
        height=300,
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def create_goal_progress_gauge(current: float, target: float):
    """Create goal progress gauge chart"""
    percentage = (current / target) * 100

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=percentage,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Goal Progress"},
        delta={'reference': 50},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "darkblue"},
               'steps': [
                   {'range': [0, 25], 'color': "lightgray"},
                   {'range': [25, 50], 'color': "gray"},
                   {'range': [50, 75], 'color': "lightblue"},
                   {'range': [75, 100], 'color': "blue"}],
               'threshold': {'line': {'color': "red", 'width': 4},
                           'thickness': 0.75, 'value': 90}}
    ))

    return fig
