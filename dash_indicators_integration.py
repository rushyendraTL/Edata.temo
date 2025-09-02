"""
Example Dash integration for the indicator summary boxes
This shows how to integrate the calculated indicators with your existing Dash dashboard
"""

import dash
from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
from visualization_factory import vv_viz_factory
import polars as pl

def create_indicator_summary_layout():
    """Create the summary indicators layout for Dash"""
    return html.Div(
        className="dashboard-summary-box",
        children=[
            html.Div(
                className="summary-indicators-container",
                children=[
                    # EV Percentage Indicator
                    html.Div(
                        className="indicator-card ev-percentage",
                        children=[
                            html.Div(
                                id="ev-percentage-value",
                                className="indicator-value",
                                children="0%"
                            ),
                            html.Div(
                                className="indicator-label",
                                children="EV Percentage"
                            )
                        ]
                    ),
                    
                    # Non-EV Percentage Indicator
                    html.Div(
                        className="indicator-card non-ev-percentage",
                        children=[
                            html.Div(
                                id="non-ev-percentage-value",
                                className="indicator-value",
                                children="0%"
                            ),
                            html.Div(
                                className="indicator-label",
                                children="Non-EV Percentage"
                            )
                        ]
                    ),
                    
                    # Top Make Indicator
                    html.Div(
                        className="indicator-card top-make",
                        children=[
                            html.Div(
                                id="top-make-value",
                                className="indicator-value",
                                children="---"
                            ),
                            html.Div(
                                id="top-make-label",
                                className="indicator-label",
                                children="Top Make"
                            )
                        ]
                    ),
                    
                    # Top Manufacturing Country Indicator
                    html.Div(
                        className="indicator-card top-country",
                        children=[
                            html.Div(
                                id="top-country-value",
                                className="indicator-value",
                                children="---"
                            ),
                            html.Div(
                                id="top-country-label",
                                className="indicator-label",
                                children="Top Country"
                            )
                        ]
                    ),
                    
                    # Total Cars Indicator
                    html.Div(
                        className="indicator-card total-cars",
                        children=[
                            html.Div(
                                id="total-cars-value",
                                className="indicator-value",
                                children="0"
                            ),
                            html.Div(
                                className="indicator-label",
                                children="Total Cars"
                            )
                        ]
                    )
                ]
            )
        ]
    )

def create_plotly_indicator_summary_layout():
    """Alternative: Create summary indicators using plotly figures"""
    return html.Div(
        className="dashboard-summary-box",
        children=[
            html.Div(
                className="summary-indicators-container",
                children=[
                    # EV Percentage Plotly Indicator
                    html.Div(
                        className="indicator-card ev-percentage",
                        children=[
                            html.Div(
                                className="plotly-indicator-container",
                                children=[
                                    dcc.Graph(
                                        id="ev-percentage-plotly",
                                        config={'displayModeBar': False},
                                        style={'height': '100%', 'width': '100%'}
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Non-EV Percentage Plotly Indicator
                    html.Div(
                        className="indicator-card non-ev-percentage",
                        children=[
                            html.Div(
                                className="plotly-indicator-container",
                                children=[
                                    dcc.Graph(
                                        id="non-ev-percentage-plotly",
                                        config={'displayModeBar': False},
                                        style={'height': '100%', 'width': '100%'}
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Top Make Plotly Indicator
                    html.Div(
                        className="indicator-card top-make",
                        children=[
                            html.Div(
                                className="plotly-indicator-container",
                                children=[
                                    dcc.Graph(
                                        id="top-make-plotly",
                                        config={'displayModeBar': False},
                                        style={'height': '100%', 'width': '100%'}
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Top Country Plotly Indicator
                    html.Div(
                        className="indicator-card top-country",
                        children=[
                            html.Div(
                                className="plotly-indicator-container",
                                children=[
                                    dcc.Graph(
                                        id="top-country-plotly",
                                        config={'displayModeBar': False},
                                        style={'height': '100%', 'width': '100%'}
                                    )
                                ]
                            )
                        ]
                    ),
                    
                    # Total Cars Plotly Indicator
                    html.Div(
                        className="indicator-card total-cars",
                        children=[
                            html.Div(
                                className="plotly-indicator-container",
                                children=[
                                    dcc.Graph(
                                        id="total-cars-plotly",
                                        config={'displayModeBar': False},
                                        style={'height': '100%', 'width': '100%'}
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

# Example callback for updating simple HTML indicators
@callback(
    [
        Output("ev-percentage-value", "children"),
        Output("non-ev-percentage-value", "children"),
        Output("top-make-value", "children"),
        Output("top-make-label", "children"),
        Output("top-country-value", "children"),
        Output("top-country-label", "children"),
        Output("total-cars-value", "children")
    ],
    [
        Input("filter-component", "value"),  # Replace with your actual filter component IDs
        # Add other filter inputs here
    ]
)
def update_indicators(filter_values):
    """Update the indicator values based on filter changes"""
    
    # Create filter_data dictionary based on your filter inputs
    filter_data = {
        'timespan': None,
        'start_date': None,
        'end_date': None,
        'country': None,
        'make': None,
        'model': None,
        'is_ev': None,
        'year_range': None,
        'pro': False,
        'pro_mode': None,
        'target_company': None,
        'top_n': 10
        # Update this based on your actual filter structure
    }
    
    try:
        # Calculate indicators using the visualization factory
        data_pl, _ = vv_viz_factory.filter_data(filter_data)
        
        # Calculate EV percentage
        ev_stats = (
            data_pl.lazy()
            .select(
                pl.col('IsEV').cast(pl.Boolean)
            )
            .group_by('IsEV')
            .agg(
                pl.len().alias('count')
            )
            .collect()
        )
        
        total_count = ev_stats['count'].sum()
        ev_count = ev_stats.filter(pl.col('IsEV') == True)['count'].sum() if len(ev_stats.filter(pl.col('IsEV') == True)) > 0 else 0
        ev_percentage = (ev_count / total_count * 100) if total_count > 0 else 0
        non_ev_percentage = 100 - ev_percentage
        
        # Get top make
        top_make_stats = (
            data_pl.lazy()
            .select(
                pl.col('Make').cast(pl.String).cast(pl.Categorical)
            )
            .group_by('Make')
            .agg(
                pl.len().alias('count')
            )
            .sort('count', descending=True)
            .limit(1)
            .collect()
        )
        
        top_make = top_make_stats['Make'][0] if len(top_make_stats) > 0 else "No Data"
        top_make_percentage = (top_make_stats['count'][0] / total_count * 100) if len(top_make_stats) > 0 and total_count > 0 else 0
        
        # Get top country
        top_country_stats = (
            data_pl.lazy()
            .select(
                pl.col('Country').cast(pl.String).cast(pl.Categorical)
            )
            .group_by('Country')
            .agg(
                pl.len().alias('count')
            )
            .sort('count', descending=True)
            .limit(1)
            .collect()
        )
        
        top_country = top_country_stats['Country'][0].upper() if len(top_country_stats) > 0 else "NO DATA"
        top_country_percentage = (top_country_stats['count'][0] / total_count * 100) if len(top_country_stats) > 0 and total_count > 0 else 0
        
        return (
            f"{ev_percentage:.1f}%",
            f"{non_ev_percentage:.1f}%",
            top_make,
            f"Top Make ({top_make_percentage:.1f}%)",
            top_country,
            f"Top Country ({top_country_percentage:.1f}%)",
            f"{total_count:,}"
        )
        
    except Exception as e:
        # Handle errors gracefully
        return "0%", "0%", "Error", "Top Make", "Error", "Top Country", "0"

# Example callback for updating plotly indicators
@callback(
    [
        Output("ev-percentage-plotly", "figure"),
        Output("non-ev-percentage-plotly", "figure"),
        Output("top-make-plotly", "figure"),
        Output("top-country-plotly", "figure"),
        Output("total-cars-plotly", "figure")
    ],
    [
        Input("filter-component", "value"),  # Replace with your actual filter component IDs
        # Add other filter inputs here
    ]
)
def update_plotly_indicators(filter_values):
    """Update the plotly indicator figures based on filter changes"""
    
    # Create filter_data dictionary based on your filter inputs
    filter_data = {
        'timespan': None,
        'start_date': None,
        'end_date': None,
        'country': None,
        'make': None,
        'model': None,
        'is_ev': None,
        'year_range': None,
        'pro': False,
        'pro_mode': None,
        'target_company': None,
        'top_n': 10
        # Update this based on your actual filter structure
    }
    
    try:
        # Generate indicators using the visualization factory methods
        ev_fig, _ = vv_viz_factory.ev_percentage_indicator(filter_data)
        non_ev_fig, _ = vv_viz_factory.non_ev_percentage_indicator(filter_data)
        top_make_fig, _ = vv_viz_factory.top_make_indicator(filter_data)
        top_country_fig, _ = vv_viz_factory.top_manufacturing_country_indicator(filter_data)
        total_cars_fig, _ = vv_viz_factory.total_cars_indicator(filter_data)
        
        # Adjust the figures for smaller container sizes
        for fig in [ev_fig, non_ev_fig, top_make_fig, top_country_fig, total_cars_fig]:
            fig.update_layout(
                height=120,
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
        
        return ev_fig, non_ev_fig, top_make_fig, top_country_fig, total_cars_fig
        
    except Exception as e:
        # Return empty figures on error
        empty_fig = go.Figure()
        empty_fig.update_layout(
            height=120,
            margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

# Example of how to integrate into your main dashboard layout
def create_full_dashboard_layout():
    """Example of complete dashboard layout with indicators"""
    return html.Div(
        className="dashboard-main-container",
        children=[
            # Header
            html.Div(
                className="dashboard-header",
                children=[
                    html.H1("Vehicle Data Dashboard"),
                    html.P("Comprehensive analytics and insights for vehicle inquiries")
                ]
            ),
            
            # Filter Bar
            html.Div(
                className="dashboard-filter-bar",
                children=[
                    # Add your filter components here
                    html.Div("Filter Controls", style={'color': 'white'})
                ]
            ),
            
            # Summary Indicators (NEW)
            create_indicator_summary_layout(),
            # OR use: create_plotly_indicator_summary_layout(),
            
            # Main Dashboard Grid
            html.Div(
                className="dashboard-custom-grid",
                children=[
                    # Your existing visualization cards
                    html.Div(
                        className="dashboard-card model-year-distribution",
                        children=[
                            html.H3("Model Year Distribution"),
                            dcc.Graph(id="model-year-chart")
                        ]
                    ),
                    # Add other cards here...
                ]
            )
        ]
    )

if __name__ == "__main__":
    print("Dash integration example for indicator summary boxes")
    print("Use create_indicator_summary_layout() or create_plotly_indicator_summary_layout() in your dashboard") 