"""
Example script demonstrating the usage of plotly indicators 
for EV percentage, non-EV percentage, top make, top manufacturing country, and total cars.
"""

from visualization_factory import vv_viz_factory
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import polars as pl

def create_indicators_dashboard():
    """Create a dashboard with all indicators"""
    
    # Sample filter data - you can modify this based on your needs
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
    }
    
    print("Generating indicators...")
    
    # Generate individual indicators
    ev_fig, ev_title = vv_viz_factory.ev_percentage_indicator(filter_data)
    non_ev_fig, non_ev_title = vv_viz_factory.non_ev_percentage_indicator(filter_data)
    top_make_fig, top_make_title = vv_viz_factory.top_make_indicator(filter_data)
    top_country_fig, top_country_title = vv_viz_factory.top_manufacturing_country_indicator(filter_data)
    total_cars_fig, total_cars_title = vv_viz_factory.total_cars_indicator(filter_data)
    
    print(f"Results:")
    print(f"- {ev_title}")
    print(f"- {non_ev_title}")
    print(f"- {top_make_title}")
    print(f"- {top_country_title}")
    print(f"- {total_cars_title}")
    
    # Show individual figures
    print("\nDisplaying individual indicators...")
    ev_fig.show()
    non_ev_fig.show()
    top_make_fig.show()
    top_country_fig.show()
    total_cars_fig.show()
    
    # Alternative: Create all indicators at once using the convenience method
    print("\nAlternative: Using create_all_indicators method...")
    all_indicators = vv_viz_factory.create_all_indicators(filter_data)
    
    for indicator_name, (fig, title) in all_indicators.items():
        print(f"{indicator_name}: {title}")
    
    return {
        'ev_percentage': (ev_fig, ev_title),
        'non_ev_percentage': (non_ev_fig, non_ev_title),
        'top_make': (top_make_fig, top_make_title),
        'top_country': (top_country_fig, top_country_title),
        'total_cars': (total_cars_fig, total_cars_title)
    }

def create_combined_dashboard():
    """Create a combined dashboard with all indicators in subplots"""
    
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
    }
    
    # Create subplot figure
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=('EV Percentage', 'Non-EV Percentage', 'Top Make', 
                       'Top Country', 'Total Cars', ''),
        specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
               [{"type": "indicator"}, {"type": "indicator"}, {"type": "xy"}]]
    )
    
    # Get data for calculations
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
    
    # Add indicators to subplots
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=ev_percentage,
        title={'text': "EV %"},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#2E8B57"}}
    ), row=1, col=1)
    
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=non_ev_percentage,
        title={'text': "Non-EV %"},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#4169E1"}}
    ), row=1, col=2)
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=top_make_percentage,
        title={'text': f"Top Make: {top_make}"},
        number={'suffix': '%'}
    ), row=1, col=3)
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=top_country_percentage,
        title={'text': f"Top Country: {top_country}"},
        number={'suffix': '%'}
    ), row=2, col=1)
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=total_count,
        title={'text': "Total Cars"},
    ), row=2, col=2)
    
    fig.update_layout(
        height=600,
        title_text="Vehicle Data Indicators Dashboard",
        title_x=0.5
    )
    
    print(f"\nCombined Dashboard Results:")
    print(f"- EV Percentage: {ev_percentage:.1f}%")
    print(f"- Non-EV Percentage: {non_ev_percentage:.1f}%")
    print(f"- Top Make: {top_make} ({top_make_percentage:.1f}%)")
    print(f"- Top Country: {top_country} ({top_country_percentage:.1f}%)")
    print(f"- Total Cars: {total_count:,}")
    
    fig.show()
    return fig

if __name__ == "__main__":
    print("Creating individual indicators...")
    indicators = create_indicators_dashboard()
    
    print("\n" + "="*50)
    print("Creating combined dashboard...")
    combined_fig = create_combined_dashboard() 