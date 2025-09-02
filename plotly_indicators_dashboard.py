"""
Complete implementation of Option 2: Plotly Indicators Dashboard
This shows how to integrate the plotly indicator methods from visualization_factory
with the new CSS styling for a professional dashboard.
"""

import dash
from dash import html, dcc, callback, Output, Input, State
import plotly.graph_objects as go
from visualization_factory import vv_viz_factory, vs_viz_factory, cmf_viz_factory
import pandas as pd
from datetime import datetime, timedelta

# Initialize the Dash app
app = dash.Dash(__name__)

def create_plotly_indicators_layout():
    """Create the summary indicators layout using plotly figures"""
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

def create_filter_bar():
    """Create the filter bar with sample filters"""
    return html.Div(
        className="dashboard-filter-bar",
        children=[
            # Dataset selector
            html.Div([
                html.Label("Dataset:", style={'color': 'white', 'margin-right': '8px'}),
                dcc.Dropdown(
                    id='dataset-selector',
                    options=[
                        {'label': 'Vehicle Valuations (VV)', 'value': 'vv'},
                        {'label': 'Vehicle Sales (VS)', 'value': 'vs'},
                        {'label': 'Claims (CMF)', 'value': 'cmf'}
                    ],
                    value='vv',
                    style={'width': '200px', 'margin-right': '20px'}
                )
            ], style={'display': 'flex', 'align-items': 'center'}),
            
            # Timespan selector
            html.Div([
                html.Label("Timespan:", style={'color': 'white', 'margin-right': '8px'}),
                dcc.Dropdown(
                    id='timespan-selector',
                    options=[
                        {'label': 'All Time', 'value': None},
                        {'label': 'Today', 'value': 'today'},
                        {'label': 'Last Week', 'value': '1w'},
                        {'label': 'Last Month', 'value': '1m'},
                        {'label': 'Last 3 Months', 'value': '3m'}
                    ],
                    value=None,
                    style={'width': '150px', 'margin-right': '20px'}
                )
            ], style={'display': 'flex', 'align-items': 'center'}),
            
            # EV Filter
            html.Div([
                html.Label("EV Only:", style={'color': 'white', 'margin-right': '8px'}),
                dcc.Checklist(
                    id='ev-filter',
                    options=[{'label': '', 'value': 'ev'}],
                    value=[],
                    style={'color': 'white'}
                )
            ], style={'display': 'flex', 'align-items': 'center'}),
            
            # Refresh button
            html.Button(
                "Refresh Data",
                id="refresh-button",
                style={
                    'background': '#4cc9f0',
                    'color': 'white',
                    'border': 'none',
                    'padding': '8px 16px',
                    'border-radius': '6px',
                    'cursor': 'pointer'
                }
            )
        ]
    )

def create_sample_charts():
    """Create some sample charts for demonstration"""
    return html.Div(
        className="dashboard-custom-grid",
        children=[
            html.Div(
                className="dashboard-card model-year-distribution",
                children=[
                    html.H3("Model Year Distribution"),
                    dcc.Graph(id="model-year-chart")
                ]
            ),
            
            html.Div(
                className="dashboard-card top-10-makes",
                children=[
                    html.H3("Top 10 Makes"),
                    dcc.Graph(id="top-makes-chart")
                ]
            ),
            
            html.Div(
                className="dashboard-card ev-composition",
                children=[
                    html.H3("EV Composition"),
                    dcc.Graph(id="ev-composition-chart")
                ]
            ),
            
            html.Div(
                className="dashboard-card model-year-price",
                children=[
                    html.H3("Model Year Price Analysis"),
                    dcc.Graph(id="model-year-price-chart")
                ]
            )
        ]
    )

# Main app layout
app.layout = html.Div(
    className="dashboard-main-container",
    children=[
        # Header
        html.Div(
            className="dashboard-header",
            children=[
                html.H1("Vehicle Data Dashboard - Plotly Indicators"),
                html.P("Real-time analytics with interactive plotly indicators")
            ]
        ),
        
        # Filter Bar
        create_filter_bar(),
        
        # Summary Indicators (Plotly Option)
        create_plotly_indicators_layout(),
        
        # Main Charts
        create_sample_charts(),
        
        # Hidden div to store filter data
        html.Div(id="filter-data-store", style={'display': 'none'})
    ]
)

# Callback to update filter data store
@app.callback(
    Output("filter-data-store", "children"),
    [
        Input("dataset-selector", "value"),
        Input("timespan-selector", "value"),
        Input("ev-filter", "value"),
        Input("refresh-button", "n_clicks")
    ]
)
def update_filter_data(dataset, timespan, ev_filter, n_clicks):
    """Create filter data dictionary from user inputs"""
    filter_data = {
        'dataset': dataset,
        'timespan': timespan,
        'start_date': None,
        'end_date': None,
        'country': None,
        'make': None,
        'model': None,
        'is_ev': 'ev' in (ev_filter or []),
        'year_range': None,
        'pro': False,
        'pro_mode': None,
        'target_company': None,
        'top_n': 10
    }
    return str(filter_data)  # Convert to string for storage

# Main callback for updating all plotly indicators
@app.callback(
    [
        Output("ev-percentage-plotly", "figure"),
        Output("non-ev-percentage-plotly", "figure"),
        Output("top-make-plotly", "figure"),
        Output("top-country-plotly", "figure"),
        Output("total-cars-plotly", "figure")
    ],
    [Input("filter-data-store", "children")]
)
def update_plotly_indicators(filter_data_str):
    """Update all plotly indicator figures based on filter changes"""
    
    try:
        # Parse filter data
        filter_data = eval(filter_data_str) if filter_data_str else {}
        
        # Select the appropriate visualization factory based on dataset
        dataset = filter_data.get('dataset', 'vv')
        if dataset == 'vs':
            viz_factory = vs_viz_factory
        elif dataset == 'cmf':
            viz_factory = cmf_viz_factory
        else:
            viz_factory = vv_viz_factory
        
        # Generate indicators using the visualization factory methods
        ev_fig, ev_title = viz_factory.ev_percentage_indicator(filter_data)
        non_ev_fig, non_ev_title = viz_factory.non_ev_percentage_indicator(filter_data)
        top_make_fig, top_make_title = viz_factory.top_make_indicator(filter_data)
        top_country_fig, top_country_title = viz_factory.top_manufacturing_country_indicator(filter_data)
        total_cars_fig, total_cars_title = viz_factory.total_cars_indicator(filter_data)
        
        # Adjust the figures for the smaller container sizes in our CSS
        indicators = [ev_fig, non_ev_fig, top_make_fig, top_country_fig, total_cars_fig]
        
        for fig in indicators:
            fig.update_layout(
                height=120,  # Match our CSS container height
                margin=dict(l=5, r=5, t=15, b=5),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(size=10, color='white'),
                # Remove axes for cleaner look in small containers
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )
            
            # For gauge charts, adjust the domain
            if hasattr(fig.data[0], 'domain'):
                fig.data[0].domain = {'x': [0.1, 0.9], 'y': [0.1, 0.9]}
        
        print(f"✅ Updated indicators:")
        print(f"   📊 {ev_title}")
        print(f"   📊 {non_ev_title}")
        print(f"   🚗 {top_make_title}")
        print(f"   🌍 {top_country_title}")
        print(f"   📈 {total_cars_title}")
        
        return ev_fig, non_ev_fig, top_make_fig, top_country_fig, total_cars_fig
        
    except Exception as e:
        print(f"❌ Error updating indicators: {e}")
        
        # Return empty figures on error
        empty_fig = go.Figure()
        empty_fig.update_layout(
            height=120,
            margin=dict(l=5, r=5, t=15, b=5),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            annotations=[
                dict(
                    text="No Data",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False,
                    font=dict(size=14, color='#b0c4de')
                )
            ],
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

# Callback for sample charts (optional - for demonstration)
@app.callback(
    [
        Output("model-year-chart", "figure"),
        Output("top-makes-chart", "figure"),
        Output("ev-composition-chart", "figure"),
        Output("model-year-price-chart", "figure")
    ],
    [Input("filter-data-store", "children")]
)
def update_sample_charts(filter_data_str):
    """Update sample charts - replace with your actual chart logic"""
    
    try:
        filter_data = eval(filter_data_str) if filter_data_str else {}
        
        dataset = filter_data.get('dataset', 'vv')
        if dataset == 'vs':
            viz_factory = vs_viz_factory
        elif dataset == 'cmf':
            viz_factory = cmf_viz_factory
        else:
            viz_factory = vv_viz_factory
        
        # Generate sample charts using your existing methods
        model_year_fig, _ = viz_factory.model_year_popularity(filter_data)
        makes_fig, _ = viz_factory.create_popularity_viz(filter_data, 'Make', viz_type='bar', orientation='vertical')
        ev_fig, _ = viz_factory.ev_composition_pie(filter_data)
        price_fig, _ = viz_factory.model_year_price_averages(filter_data)
        
        return model_year_fig, makes_fig, ev_fig, price_fig
        
    except Exception as e:
        print(f"❌ Error updating charts: {e}")
        empty_fig = go.Figure()
        return empty_fig, empty_fig, empty_fig, empty_fig

# Custom CSS to ensure our stylesheet is loaded
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="stylesheet" href="/assets/css/attractive_bi.css">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == "__main__":
    print("🚀 Starting Plotly Indicators Dashboard...")
    print("📊 Features:")
    print("   ✅ EV Percentage Gauge")
    print("   ✅ Non-EV Percentage Gauge") 
    print("   ✅ Top Make Indicator")
    print("   ✅ Top Manufacturing Country Indicator")
    print("   ✅ Total Cars Counter")
    print("   ✅ Responsive CSS styling")
    print("   ✅ Real-time updates")
    print("\n🌐 Dashboard will be available at: http://127.0.0.1:8050")
    
    app.run_server(debug=True, port=8050) 