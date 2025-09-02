from data import vv, vs, start_date, end_date, make_country_map, country_iso, year_ranges_enum, price_ranges_enum, cmf
from datetime import datetime, timedelta, date
import plotly.express as px
import dash
from dash import dash_table
from dash_table import DataTable, FormatTemplate
import plotly.io as pio
import plotly.graph_objects as go
import pandas as pd
import polars as pl
from plotly.subplots import make_subplots
import pycountry
pct_format = FormatTemplate.percentage(2)

# Global configuration
GLOBAL_FONT_FAMILY = '"Ancizar Sans", sans-serif'
GLOBAL_FONT_CONFIG = dict(family=GLOBAL_FONT_FAMILY)

# Define and register the FiveThirtyEight-like template for Plotly


# def set_fivethirtyeight_plotly_template():
#     fivethirtyeight_template = go.layout.Template()

#     # Matplotlib style: axes.prop_cycle: cycler('color', ['008fd5', 'fc4f30', 'e5ae38', '6d904f', '8b8b8b', '810f7c'])
#     colors_538 = ['#008fd5', '#fc4f30', '#e5ae38',
#                   '#6d904f', '#8b8b8b', '#810f7c']

#     fivethirtyeight_template.layout = go.Layout(
#         # Matplotlib style: font.size:14.0
#         font=dict(size=14, family="Arial, sans-serif"),
#         title=dict(
#             # Matplotlib style: axes.titlesize: x-large (approx 24px for base 14px)
#             font=dict(size=24, family="Arial Black, Arial, sans-serif",
#                       color='#333333'),
#             x=0.05,  # Align title to the left, common in 538 style
#             xanchor='left'
#         ),
#         # Matplotlib style: axes.facecolor: f0f0f0
#         # plot_bgcolor='#f0f0f0',
#         # Matplotlib style: figure.facecolor: f0f0f0 / savefig.facecolor: f0f0f0
#         # paper_bgcolor='#f0f0f0',
#         colorway=colors_538,
#         # Matplotlib style: figure.subplot.left: 0.08, figure.subplot.right: 0.95, figure.subplot.bottom: 0.07
#         # Translated to margins: l=56, r=35, b=35 (assuming ~700px width, ~500px height), t=80 for title
#         margin=dict(l=56, r=35, t=80, b=35),

#         xaxis=dict(
#             # Matplotlib style: axes.grid: true
#             showgrid=True,
#             # Matplotlib style: grid.color: cbcbcb
#             gridcolor='#cbcbcb',
#             # Matplotlib style: grid.linewidth: 1.0
#             gridwidth=1.0,
#             # Matplotlib style: grid.linestyle: - (solid)
#             griddash='solid',
#             # Matplotlib style: axes.edgecolor: f0f0f0
#             linecolor='#f0f0f0',
#             showline=True,
#             # Matplotlib style: axes.linewidth: 3.0
#             linewidth=3.0,
#             # Matplotlib style: xtick.major.size: 0 / xtick.minor.size: 0
#             ticklen=0,
#             # Matplotlib style: axes.axisbelow: true
#             layer='below traces',
#             # Matplotlib style: axes.labelsize: large (approx 17px for base 14px)
#             title_font=dict(size=17, family="Arial, sans-serif"),
#             zeroline=False,
#             automargin=True
#         ),
#         yaxis=dict(
#             showgrid=True,
#             gridcolor='#cbcbcb',
#             gridwidth=1.0,
#             griddash='solid',
#             linecolor='#f0f0f0',
#             showline=True,
#             linewidth=3.0,
#             ticklen=0,
#             layer='below traces',
#             title_font=dict(size=17, family="Arial, sans-serif"),
#             zeroline=False,
#             automargin=True
#         ),
#         legend=dict(
#             # Matplotlib style: legend.fancybox: true (approximated)
#             bordercolor='#cccccc',
#             borderwidth=1,
#             # Slightly transparent version of papercolor
#             bgcolor='rgba(240,240,240,0.8)',
#             font=dict(size=12)
#         )
#     )

#     # Matplotlib style: lines.linewidth: 4
#     # lines.solid_capstyle: butt - Plotly's default line endings are generally clean.
#     fivethirtyeight_template.data.scatter = [go.Scatter(line=dict(width=4))]

#     # Matplotlib style: patch.edgecolor: f0f0f0, patch.linewidth: 0.5
#     bar_marker_line = dict(color='#f0f0f0', width=0.5)
#     fivethirtyeight_template.data.bar = [go.Bar(marker_line=bar_marker_line)]
#     fivethirtyeight_template.data.histogram = [
#         go.Histogram(marker_line=bar_marker_line)]
#     # Could add for other trace types like pie if needed:
#     # fivethirtyeight_template.data.pie = [go.Pie(marker_line=bar_marker_line)]

#     pio.templates['fivethirtyeight_custom'] = fivethirtyeight_template
#     # Apply this template on top of Plotly's defaults
#     pio.templates.default = 'plotly+fivethirtyeight_custom'


# Call the function to set the template when this module is loaded
# set_fivethirtyeight_plotly_template()


class VisualizationFactory:
    def __init__(self, data, end_date=end_date, start_date=start_date, date_col='InquiryDate'):
        self.data = data
        self.end_date = end_date
        self.start_date = start_date
        self.date_col = date_col

    def _apply_global_layout(self, fig):
        """Helper method to apply global layout settings to figures"""
        fig.update_layout(
            font=GLOBAL_FONT_CONFIG,
            template='plotly_white',
            xaxis_title=None,  # Hide x-axis title
            yaxis_title=None,  # Hide y-axis title
        )
        return fig

    # === TEMPORAL COMPARISON HELPER FUNCTIONS ===

    def _calculate_time_period_duration(self, filter_data):
        """
        Calculate duration of current time period from filter_data
        Returns: (start_date, end_date, duration_days, period_type)
        """
        today = datetime.today()

        # Use data end_date as the effective "today" for calculations
        effective_today = min(self.end_date, today)

        # Priority 1: Custom date range
        if filter_data.get('start_date') and filter_data.get('end_date'):
            start_date = filter_data['start_date']
            end_date = filter_data['end_date']
            if isinstance(start_date, str):
                start_date = datetime.fromisoformat(
                    start_date.replace('Z', '+00:00')).replace(tzinfo=None)
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(
                    end_date.replace('Z', '+00:00')).replace(tzinfo=None)
            duration_days = (end_date - start_date).days
            return start_date, end_date, duration_days, "custom"

        # Priority 2: Timespan buttons
        if filter_data.get('timespan'):
            timespan = filter_data['timespan']
            if timespan == 'today':
                start_date = datetime.combine(
                    effective_today.date(), datetime.min.time())
                end_date = datetime.combine(
                    effective_today.date(), datetime.max.time())
                return start_date, end_date, 1, "today"
            elif timespan == '1w':
                end_date = effective_today
                start_date = end_date - timedelta(days=7)
                return start_date, end_date, 7, "1w"
            elif timespan == '1m':
                end_date = effective_today
                start_date = end_date - timedelta(days=30)
                return start_date, end_date, 30, "1m"
            elif timespan == '3m':
                end_date = effective_today
                start_date = end_date - timedelta(days=90)
                return start_date, end_date, 90, "3m"

        # Priority 3: Default (1 month)
        end_date = effective_today
        start_date = end_date - timedelta(days=30)
        return start_date, end_date, 30, "1m"

    def _generate_smart_period_labels(self, start_date, end_date, is_current=True, period_type=None):
        """
        Generate smart labels like 'This month', 'These 3 months', etc.
        """
        duration_days = (end_date - start_date).days
        prefix = "This" if is_current else "Last"

        # Use period_type if available for more accurate labeling
        if period_type:
            if period_type == "today":
                return f"{prefix} day"
            elif period_type == "1w":
                return f"{prefix} week"
            elif period_type == "1m":
                return f"{prefix} month"
            elif period_type == "3m":
                prefix = "These" if is_current else "Last"
                return f"{prefix} 3 months"

        # Fallback to duration-based logic
        if duration_days <= 1:
            return f"{prefix} day"
        elif duration_days <= 7:
            return f"{prefix} week"
        elif duration_days <= 31:
            return f"{prefix} month"
        elif duration_days <= 93:  # ~3 months
            months = round(duration_days / 30)
            if months == 1:
                return f"{prefix} month"
            prefix = "These" if is_current else "Last"
            return f"{prefix} {months} months"
        else:
            months = round(duration_days / 30)
            prefix = "These" if is_current else "Last"
            return f"{prefix} {months} months"

    def _create_temporal_segments_with_fallback(self, data_pl, filter_data, current_start, current_end, period_type=None):
        """
        Create temporal segments with fallback logic
        Returns: (segmented_data, current_label, previous_label)
        """
        company = filter_data.get('target_company')
        duration_days = (current_end - current_start).days

        # Calculate previous period
        previous_start = current_start - timedelta(days=duration_days)
        previous_end = current_start

        # EFFICIENT: Check against data bounds instead of querying data
        if previous_start < self.start_date:
            # Previous period extends before available data
            # Calculate how much of the previous period is actually available
            available_previous_days = (current_start - self.start_date).days

            # Less than 10% overlap
            if available_previous_days < (duration_days * 0.1):
                # Apply fallback: divide current period by 2
                new_duration = duration_days // 2
                if new_duration < 1:
                    # Minimum reached - return current period only
                    return self._create_single_period_segment(data_pl, filter_data, current_start, current_end, period_type)

                # Recursive call with smaller period - lose period_type since it's no longer accurate
                new_current_start = current_end - timedelta(days=new_duration)
                return self._create_temporal_segments_with_fallback(
                    data_pl, filter_data, new_current_start, current_end, period_type=None
                )

        # Previous period is viable - create segments
        return self._create_dual_period_segments(data_pl, filter_data, previous_start, current_start, current_end, period_type)

    def _create_dual_period_segments(self, data_pl, filter_data, previous_start, current_start, current_end, period_type=None):
        """Create segments for both current and previous periods"""
        company = filter_data.get('target_company')
        company_data = data_pl.filter(pl.col('CompanyName') == company)

        segmented_data = company_data.with_columns(
            pl.when((pl.col(self.date_col) >= current_start)
                    & (pl.col(self.date_col) <= current_end))
            .then(pl.lit('Current Period'))
            .when((pl.col(self.date_col) >= previous_start) & (pl.col(self.date_col) < current_start))
            .then(pl.lit('Previous Period'))
            .otherwise(None)
            .alias('segment')
        ).filter(pl.col('segment').is_not_null())

        # Generate labels
        current_label = self._generate_smart_period_labels(
            current_start, current_end, is_current=True, period_type=period_type)
        previous_label = self._generate_smart_period_labels(
            previous_start, current_start, is_current=False, period_type=period_type)

        return segmented_data, current_label, previous_label

    def _create_single_period_segment(self, data_pl, filter_data, current_start, current_end, period_type=None):
        """Fallback: create single period when no previous data available"""
        company = filter_data.get('target_company')
        company_data = data_pl.filter(pl.col('CompanyName') == company)

        segmented_data = company_data.filter(
            pl.col(self.date_col) >= current_start
        ).with_columns(
            pl.lit('Current Period').alias('segment')
        )

        current_label = self._generate_smart_period_labels(
            current_start, current_end, is_current=True, period_type=period_type)

        return segmented_data, current_label, "No Previous Data"

    def filter_data(self, filter_data):
        data_to_filter = self.data

        # Convert date column to datetime at the start
        data_to_filter = data_to_filter.with_columns(
            pl.col(self.date_col).str.to_datetime('%Y-%m-%d %H:%M:%S')
        )

        if filter_data.get('pro'):
            company = filter_data.get('target_company')
            pro_mode = filter_data.get('pro_mode', 'benchmark')
            print('company:', company)

            if pro_mode == 'temporal_comparison':
                # NEW: Temporal comparison logic
                if company:
                    # Calculate current time period
                    current_start, current_end, duration_days, period_type = self._calculate_time_period_duration(
                        filter_data)

                    # Create temporal segments with fallback
                    data_to_filter, current_label, previous_label = self._create_temporal_segments_with_fallback(
                        data_to_filter, filter_data, current_start, current_end, period_type
                    )

                    # Store labels for later use in visualizations
                    filter_data['_temporal_current_label'] = current_label
                    filter_data['_temporal_previous_label'] = previous_label
                else:
                    # No company specified - create empty segment
                    data_to_filter = data_to_filter.with_columns(
                        pl.lit('Current Period').alias('segment')
                    )
            else:
                # EXISTING: Benchmark/market_share logic
                if company:
                    data_to_filter = data_to_filter.filter(
                        pl.col('CompanyName').is_not_null()
                    )
                    data_to_filter = data_to_filter.with_columns(
                        pl.when(pl.col('CompanyName') == company)
                        .then(pl.lit(company))
                        .otherwise(pl.lit('Market'))
                        .alias('segment')
                    )
                else:
                    data_to_filter = data_to_filter.with_columns(
                        pl.lit('Market').alias('segment')
                    )

        # Skip normal time filtering for temporal comparison mode - it handles its own time filtering
        is_temporal_comparison = filter_data.get(
            'pro') and filter_data.get('pro_mode') == 'temporal_comparison'

        if filter_data.get('timespan') and not is_temporal_comparison:
            timespan = filter_data.get('timespan')
            today = datetime.today()
            if timespan == 'today':
                today = min(self.end_date, datetime.today())
                today_start = datetime.combine(
                    today.date(), datetime.min.time())
                today_end = datetime.combine(today.date(), datetime.max.time())
                data_to_filter = data_to_filter.filter(
                    (pl.col(self.date_col) >= today_start) &
                    (pl.col(self.date_col) <= today_end)
                )
            elif timespan == '1w':
                start_date = today - timedelta(days=7)
                start_date = min(self.end_date - timedelta(days=7), start_date)
                data_to_filter = data_to_filter.filter(
                    pl.col(self.date_col) >= start_date
                )
            elif timespan == '1m':
                start_date = today - timedelta(days=30)
                start_date = min(
                    self.end_date - timedelta(days=30), start_date)
                data_to_filter = data_to_filter.filter(
                    pl.col(self.date_col) >= start_date
                )
            elif timespan == '3m':
                start_date = today - timedelta(days=90)
                start_date = min(
                    self.end_date - timedelta(days=90), start_date)
                data_to_filter = data_to_filter.filter(
                    pl.col(self.date_col) >= start_date
                )

        if not filter_data.get('pro') and not filter_data.get('pro_mode'):
            if filter_data.get('start_date') and filter_data.get('end_date'):
                start_date = filter_data['start_date']
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = filter_data['end_date']
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                if start_date > end_date:
                    start_date, end_date = end_date, start_date
                data_to_filter = data_to_filter.filter(
                    (pl.col(self.date_col) >= start_date) &
                    (pl.col(self.date_col) <= end_date)
                )
            elif filter_data.get('start_date'):
                start_date = filter_data['start_date']
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                data_to_filter = data_to_filter.filter(
                    pl.col(self.date_col) >= start_date
                )
            elif filter_data.get('end_date'):
                end_date = filter_data['end_date']
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                data_to_filter = data_to_filter.filter(
                    pl.col(self.date_col) <= end_date
                )

        if filter_data.get('country'):
            countries = filter_data['country']
            data_to_filter = data_to_filter.with_columns(
                pl.col('Country').cast(pl.Categorical)
            ).filter(
                pl.col('Country').is_in(countries)
            )

        if filter_data.get('make'):
            makes = filter_data['make']
            data_to_filter = data_to_filter.with_columns(
                pl.col('Make').cast(pl.Categorical)
            ).filter(
                pl.col('Make').is_in(makes)
            )

        if filter_data.get('model'):
            models = filter_data['model']
            data_to_filter = data_to_filter.with_columns(
                pl.col('Model').cast(pl.Categorical)
            ).filter(
                pl.col('Model').is_in(models)
            )

        if filter_data.get('is_ev'):
            data_to_filter = data_to_filter.filter(pl.col('IsEV'))

        if filter_data.get('year_range'):
            year_range = filter_data['year_range']
            min_year, max_year = year_range
            data_to_filter = data_to_filter.with_columns(
                pl.col('ModelYear').cast(pl.Int32).fill_null(2000)
            ).filter(
                (pl.col('ModelYear') >= min_year) &
                (pl.col('ModelYear') <= max_year)
            )

        top_n = filter_data.get('top_n', 10)
        return data_to_filter, top_n

    def model_year_popularity(self, filter_data):
        data, top_n = self.filter_data(filter_data)
        
        # Use Polars operations instead of pandas
        model_year_counts = (
            data.lazy()
            .select(
                pl.col('ModelYear').cast(pl.Int32)
            )
            .group_by('ModelYear')
            .agg(
                pl.len().alias('count')
            )
            .sort('count', descending=True)
            .limit(top_n)
            .collect()
            .to_pandas()
        )

        # Check if we have data
        if model_year_counts.empty:
            fig = go.Figure()
            fig.update_layout(margin=dict(l=2, r=2, t=5, b=2))
            self._apply_global_layout(fig)
            title_str = f'Top {top_n} Model Years - No Data'
            return fig, title_str

        # Ensure ModelYear is treated as categorical strings for px.bar
        model_year_counts['ModelYear'] = model_year_counts['ModelYear'].astype(str)

        model_years = model_year_counts['ModelYear']
        counts = model_year_counts['count']
        total_counts = counts.sum()
        normalized_counts = (counts / total_counts) * 100
        bar_width = 0.5
        fig = go.Figure()

        fig.add_trace(go.Bar(x=model_years, y=normalized_counts,
                             text=normalized_counts, textposition='outside', width=bar_width))

        fig.update_traces(texttemplate='%{text:.0f}%', textposition='outside')
        fig.update_yaxes(showticklabels=False)

        max_y_value = normalized_counts.max()
        fig.update_yaxes(range=[0, max_y_value * 1.15])

        title_str = f'Top {top_n} Model Years'

        fig.update_layout(margin=dict(l=2, r=2, t=5, b=2))
        self._apply_global_layout(fig)

        return fig, title_str

    def create_popularity_viz(
        self,
        filter_data,
        grouping_column,
        viz_type="bar",
        orientation="vertical",
        pro=False,
    ):
        data, top_n = self.filter_data(filter_data)
        pro = filter_data.get('pro', False)
        pro_mode = filter_data.get('pro_mode', 'benchmark')
        print('pro:', pro)

        primary_color = '#0466C8'
        secondary_color = '#4cc9f0'
        if viz_type == 'line':
            top_n = 100

        # First identify top categories based on total counts (popularity)
        if pro:
            top_categories = (
                data.lazy()
                .group_by(grouping_column)
                .agg(pl.len().alias('total_count'))
                .sort('total_count', descending=True)
                .limit(top_n)
                .select(pl.col(grouping_column))
            )

            # Now get the pro data only for these top categories
            grouped_data = (
                data.lazy()
                .join(top_categories, on=grouping_column, how='inner')
                .select(
                    pl.col('segment').cast(pl.String).cast(pl.Categorical),
                    pl.col(grouping_column).cast(
                        pl.String).cast(pl.Categorical)
                )
                .group_by(
                    pl.col('segment'),
                    pl.col(grouping_column)
                )
                .agg(
                    pl.col(grouping_column).count().alias('count')
                )
            )

        else:
            grouped_data = (
                data.lazy()
                .select(
                    pl.col(grouping_column).cast(
                        pl.String).cast(pl.Categorical)
                )
                .group_by(
                    pl.col(grouping_column)
                )
                .agg(
                    pl.col(grouping_column).count().alias('count')
                )
            )

        text_position = 'outside'

        # Normalization
        if pro:
            if pro_mode == 'benchmark' or pro_mode == 'temporal_comparison':
                # Both use same normalization: percentage within each segment
                segment_sums = grouped_data.group_by('segment').agg(
                    pl.col('count').sum().alias('sum')
                )
                grouped_data = grouped_data.join(segment_sums, on='segment')
                grouped_data = grouped_data.select(
                    pl.col('segment'),
                    pl.col(grouping_column),
                    normalized_count=(pl.col('count') /
                                      pl.col('sum') * 100).cast(pl.Float32)
                )

                barmode = 'group'
                text_position = 'outside'
            elif pro_mode == 'market_share':
                grouped_data = grouped_data.with_columns(
                    normalized_count=(
                        pl.col('count') / pl.col('count').sum() * 100).cast(pl.Float32)
                )
                barmode = 'stack'
                text_position = 'outside'

            color_column = 'segment'

            # Set colors based on pro_mode
            if pro_mode == 'temporal_comparison':
                color_discrete_map = {
                    'Current Period': secondary_color,  # Highlight current
                    'Previous Period': primary_color
                }
            else:
                color_discrete_map = {
                    'Market': primary_color,
                    filter_data.get('target_company'): secondary_color
                }
        else:
            grouped_data = grouped_data.with_columns(
                normalized_count=(pl.col('count') /
                                  pl.col('count').sum() * 100).cast(pl.Float32)
            )
            barmode = None
            color_column = None
            color_discrete_map = None

        fig = go.Figure()

        if viz_type == "bar":
            if pro:
                # For pro mode, we've already filtered to top_n categories
                grouped_data = grouped_data.sort(
                    by='normalized_count', descending=True
                ).collect().to_pandas()
            else:
                grouped_data = grouped_data.sort(
                    by='normalized_count', descending=True
                ).limit(top_n).collect().to_pandas()

            bar_width = 0.5

            if orientation == "vertical":
                x = grouping_column
                y = 'normalized_count'
                text = 'normalized_count'
                orientation = "v"
            else:
                x = 'normalized_count'
                y = grouping_column
                text = 'normalized_count'
                orientation = "h"

            fig = px.bar(
                data_frame=grouped_data,
                x=x,
                y=y,
                text=text,
                orientation=orientation,
                color=color_column,
                barmode=barmode,
                color_discrete_map=color_discrete_map
            )
            if not pro:  # Apply primary color directly if not in pro mode
                fig.update_traces(marker_color=primary_color)
                fig.update_traces(width=bar_width)

            fig.update_traces(
                texttemplate='%{text:.0f}%', textposition=text_position)

            if orientation == 'v':
                fig.update_yaxes(showticklabels=False)
                if not grouped_data.empty:
                    if pro and pro_mode == 'market_share':
                        max_y_value = grouped_data.groupby(grouping_column)[
                            'normalized_count'].sum().max()
                    else:
                        max_y_value = grouped_data['normalized_count'].max()

                    if pd.notna(max_y_value) and max_y_value > 0:
                        fig.update_yaxes(range=[0, max_y_value * 1.15])
                    else:
                        fig.update_yaxes(range=[0, 1])
                else:
                    fig.update_yaxes(range=[0, 1])

                # fig.update_layout(xaxis={
                #     'categoryorder': 'total descending'
                # })
                fig.update_layout(xaxis={
                    'categoryorder': 'array',
                    'categoryarray': grouped_data[grouping_column].tolist()[::-1]
                })
            else:  # orientation == 'h'
                fig.update_xaxes(showticklabels=False)
                if not grouped_data.empty:
                    if pro and pro_mode == 'market_share':
                        max_x_value = grouped_data.groupby(grouping_column)[
                            'normalized_count'].sum().max()
                    else:
                        max_x_value = grouped_data['normalized_count'].max()

                    if pd.notna(max_x_value) and max_x_value > 0:
                        fig.update_xaxes(range=[0, max_x_value * 1.15])
                    else:
                        fig.update_xaxes(range=[0, 1])
                else:
                    fig.update_xaxes(range=[0, 1])

                fig.update_layout(yaxis={
                    'categoryorder': 'array',
                    'categoryarray': grouped_data[grouping_column].tolist()
                })

            title = f'Top {top_n} {grouping_column}'
        elif viz_type == "line":
            grouped_data = grouped_data.sort(
                by=grouping_column, descending=False).collect().to_pandas()
            grouped_data[grouping_column] = grouped_data[grouping_column].astype(
                int)
            grouped_data = grouped_data.sort_values(
                by=grouping_column, ascending=False)
            fig = px.line(grouped_data, x=grouping_column,
                          y='normalized_count', text='normalized_count', color=color_column,
                          color_discrete_map=color_discrete_map)
            if not pro:  # Apply primary color directly if not in pro mode
                fig.update_traces(line_color=primary_color)

            fig.update_traces(
                texttemplate='%{text:.0f}%', textposition='top center')
            fig.update_yaxes(showticklabels=False)
            max_y_value = grouped_data['normalized_count'].max()
            fig.update_yaxes(range=[0, max_y_value * 1.15])
            title = f'Trend of {grouping_column}'
        else:
            raise ValueError(f"Invalid viz_type: {viz_type}")

        # Adjust margins based on chart type and orientation to prevent text cutoff
        if viz_type == "bar" and orientation == "vertical":
            # For vertical bar charts, need more right margin for percentage labels
            margin_settings = dict(l=5, r=45, t=10, b=40)
        else:
            # Default margins for other chart types
            margin_settings = dict(l=2, r=2, t=5, b=2)
            
        fig.update_layout(
            margin=margin_settings,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        # Update legend labels for temporal comparison mode
        if pro and pro_mode == 'temporal_comparison':
            current_label = filter_data.get(
                '_temporal_current_label', 'Current Period')
            previous_label = filter_data.get(
                '_temporal_previous_label', 'Previous Period')

            # Update legend labels to show smart time period labels
            for trace in fig.data:
                if trace.name == 'Current Period':
                    trace.name = current_label
                elif trace.name == 'Previous Period':
                    trace.name = previous_label

        self._apply_global_layout(fig)
        return fig, title

    def create_summary_viz(
        self,
        filter_data,
        grouping_column,
        summary_column,
        summary_function="sum",  # "sum", "mean", "median", "count"
        viz_type="bar",
        orientation="vertical",
        pro=False,
    ):
        data, top_n = self.filter_data(filter_data)
        pro = filter_data.get('pro', False)
        pro_mode = filter_data.get('pro_mode', 'benchmark')
        print('pro:', pro)

        primary_color = '#0466C8'
        secondary_color = '#4cc9f0'
        if viz_type == 'line':
            top_n = 100

        # Define aggregation expression based on summary_function
        if summary_function == "sum":
            agg_expr = pl.col(summary_column).cast(
                pl.Float64).sum().alias('summary_value')
        elif summary_function == "mean":
            agg_expr = pl.col(summary_column).cast(
                pl.Float64).mean().alias('summary_value')
        elif summary_function == "median":
            agg_expr = pl.col(summary_column).cast(
                pl.Float64).median().alias('summary_value')
        elif summary_function == "count":
            agg_expr = pl.len().alias('summary_value')
        else:
            raise ValueError(
                f"Invalid summary_function: {summary_function}. Must be one of: sum, mean, median, count")

        # First identify top categories based on total counts (popularity)
        if pro:
            top_categories = (
                data.lazy()
                .group_by(grouping_column)
                .agg(pl.len().alias('total_count'))
                .sort('total_count', descending=True)
                .limit(top_n)
                .select(pl.col(grouping_column))
            )

            # Now get the pro data only for these top categories
            grouped_data = (
                data.lazy()
                .join(top_categories, on=grouping_column, how='inner')
                .select(
                    pl.col('segment').cast(pl.String).cast(pl.Categorical),
                    pl.col(grouping_column).cast(
                        pl.String).cast(pl.Categorical),
                    pl.col(summary_column)
                )
                .group_by(
                    pl.col('segment'),
                    pl.col(grouping_column)
                )
                .agg(agg_expr)
                .filter(pl.col('summary_value').is_not_null())
            )
        else:
            grouped_data = (
                data.lazy()
                .select(
                    pl.col(grouping_column).cast(
                        pl.String).cast(pl.Categorical),
                    pl.col(summary_column)
                )
                .group_by(
                    pl.col(grouping_column)
                )
                .agg(agg_expr)
                .filter(pl.col('summary_value').is_not_null())
            )

        text_position = 'outside'

        if pro:
            if pro_mode == 'benchmark' or pro_mode == 'temporal_comparison':
                # Both use same normalization: percentage within each segment
                segment_sums = grouped_data.group_by('segment').agg(
                    pl.col('summary_value').sum().alias('sum')
                )
                grouped_data = grouped_data.join(segment_sums, on='segment')
                grouped_data = grouped_data.select(
                    pl.col('segment'),
                    pl.col(grouping_column),
                    normalized_summary=(pl.col('summary_value') /
                                        pl.col('sum') * 100).cast(pl.Float32)
                )

                barmode = 'group'
                text_position = 'outside'
            elif pro_mode == 'market_share':
                grouped_data = grouped_data.with_columns(
                    normalized_summary=(
                        pl.col('summary_value') / pl.col('summary_value').sum() * 100).cast(pl.Float32)
                )
                barmode = 'stack'
                text_position = 'outside'

            color_column = 'segment'

            # Set colors based on pro_mode
            if pro_mode == 'temporal_comparison':
                color_discrete_map = {
                    'Current Period': secondary_color,  # Highlight current
                    'Previous Period': primary_color
                }
            else:
                color_discrete_map = {
                    'Market': primary_color,
                    filter_data.get('target_company'): secondary_color
                }
        else:
            grouped_data = grouped_data.with_columns(
                normalized_summary=(pl.col('summary_value') /
                                    pl.col('summary_value').sum() * 100).cast(pl.Float32)
            )
            barmode = None
            color_column = None
            color_discrete_map = None

        fig = go.Figure()

        if viz_type == "bar":
            if pro:
                # For pro mode, we've already filtered to top_n categories
                grouped_data = grouped_data.sort(
                    by='normalized_summary', descending=True
                ).collect().to_pandas()
            else:
                grouped_data = grouped_data.sort(
                    by='normalized_summary', descending=True
                ).limit(top_n).collect().to_pandas()

            bar_width = 0.5

            if orientation == "vertical":
                x = grouping_column
                y = 'normalized_summary'
                text = 'normalized_summary'
                orientation = "v"
            else:
                x = 'normalized_summary'
                y = grouping_column
                text = 'normalized_summary'
                orientation = "h"

            fig = px.bar(
                data_frame=grouped_data,
                x=x,
                y=y,
                text=text,
                orientation=orientation,
                color=color_column,
                barmode=barmode,
                color_discrete_map=color_discrete_map
            )
            if not pro:  # Apply primary color directly if not in pro mode
                fig.update_traces(marker_color=primary_color)
                fig.update_traces(width=bar_width)

            fig.update_traces(
                texttemplate='%{text:.0f}%', textposition=text_position)

            if orientation == 'v':
                fig.update_yaxes(showticklabels=False)
                if not grouped_data.empty:
                    if pro and pro_mode == 'market_share':
                        max_y_value = grouped_data.groupby(grouping_column)[
                            'normalized_summary'].sum().max()
                    else:
                        max_y_value = grouped_data['normalized_summary'].max()

                    if pd.notna(max_y_value) and max_y_value > 0:
                        fig.update_yaxes(range=[0, max_y_value * 1.15])
                    else:
                        fig.update_yaxes(range=[0, 1])
                else:
                    fig.update_yaxes(range=[0, 1])

                # Set explicit category order based on our sorted data
                fig.update_layout(xaxis={
                    'categoryorder': 'array',
                    'categoryarray': grouped_data[grouping_column].tolist()
                })
            else:  # orientation == 'h'
                fig.update_xaxes(showticklabels=False)
                if not grouped_data.empty:
                    if pro and pro_mode == 'market_share':
                        max_x_value = grouped_data.groupby(grouping_column)[
                            'normalized_summary'].sum().max()
                    else:
                        max_x_value = grouped_data['normalized_summary'].max()

                    if pd.notna(max_x_value) and max_x_value > 0:
                        fig.update_xaxes(range=[0, max_x_value * 1.15])
                    else:
                        fig.update_xaxes(range=[0, 1])
                else:
                    fig.update_xaxes(range=[0, 1])

                # Set explicit category order based on our sorted data (reversed for horizontal)
                fig.update_layout(yaxis={
                    'categoryorder': 'array',
                    'categoryarray': grouped_data[grouping_column].tolist()[::-1]
                })

            title = f'Top {top_n} {grouping_column} by {summary_function.title()} of {summary_column}'
        elif viz_type == "line":
            grouped_data = grouped_data.sort(
                by=grouping_column, descending=False).collect().to_pandas()
            grouped_data[grouping_column] = grouped_data[grouping_column].astype(
                int)
            grouped_data = grouped_data.sort_values(
                by=grouping_column, ascending=False)
            fig = px.line(grouped_data, x=grouping_column,
                          y='normalized_summary', text='normalized_summary', color=color_column,
                          color_discrete_map=color_discrete_map)
            if not pro:  # Apply primary color directly if not in pro mode
                fig.update_traces(line_color=primary_color)

            fig.update_traces(
                texttemplate='%{text:.0f}%', textposition='top center')
            fig.update_yaxes(showticklabels=False)
            max_y_value = grouped_data['normalized_summary'].max()
            fig.update_yaxes(range=[0, max_y_value * 1.15])
            title = f'Trend of {grouping_column} by {summary_function.title()} of {summary_column}'
        else:
            raise ValueError(f"Invalid viz_type: {viz_type}")

        fig.update_layout(
            margin=dict(l=2, r=2, t=5, b=2),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        # Update legend labels for temporal comparison mode
        if pro and pro_mode == 'temporal_comparison':
            current_label = filter_data.get(
                '_temporal_current_label', 'Current Period')
            previous_label = filter_data.get(
                '_temporal_previous_label', 'Previous Period')

            # Update legend labels to show smart time period labels
            for trace in fig.data:
                if trace.name == 'Current Period':
                    trace.name = current_label
                elif trace.name == 'Previous Period':
                    trace.name = previous_label

        self._apply_global_layout(fig)
        return fig, title

    def model_year_price_averages(self, filter_data):
        data_pl, _ = self.filter_data(filter_data)
        pro = filter_data.get('pro', False)
        pro_mode = filter_data.get('pro_mode', 'benchmark')

        primary_color = '#0466C8'
        secondary_color = '#4cc9f0'

        # Base aggregation for both pro and non-pro modes
        price_trends = (
            data_pl.lazy()
            .select(
                pl.col('ModelYear').cast(pl.Int32),
                pl.col('Price'),
                pl.col('segment').cast(pl.String).cast(
                    pl.Categorical) if pro else pl.lit('Market').alias('segment')
            )
            .group_by(['segment', 'ModelYear'])
            .agg(
                pl.col('Price').mean().alias('Price')
            )
            .sort('ModelYear')
        )

        if pro:
            if pro_mode == 'benchmark' or pro_mode == 'temporal_comparison':
                # Both use same normalization: percentage within each segment
                trends_pd = price_trends.collect().to_pandas()
                color_column = 'segment'
            elif pro_mode == 'market_share':
                # Calculate market prices
                market_prices = (
                    price_trends
                    .filter(pl.col('segment') == 'Market')
                    .select(
                        pl.col('ModelYear'),
                        pl.col('Price').alias('market_price')
                    )
                )

                # Calculate relative difference from market average
                trends_pd = (
                    price_trends
                    .filter(pl.col('segment') != 'Market')
                    .join(market_prices, on='ModelYear', how='left')
                    .with_columns(
                        Price=((pl.col('Price') - pl.col('market_price')
                                ) / pl.col('market_price') * 100)
                    )
                    .select(['ModelYear', 'segment', 'Price'])
                    .collect()
                    .to_pandas()
                )
                color_column = 'segment'
        else:
            trends_pd = price_trends.collect().to_pandas()
            color_column = None

        # Create the visualization
        color_discrete_map = None
        if pro:
            if pro_mode == 'temporal_comparison':
                color_discrete_map = {
                    'Current Period': secondary_color,
                    'Previous Period': primary_color
                }
            else:
                color_discrete_map = {
                    'Market': primary_color,
                    filter_data.get('target_company'): secondary_color
                }

        fig = px.line(
            trends_pd,
            x='ModelYear',
            y='Price',
            color=color_column,
            color_discrete_map=color_discrete_map,
            markers=True
        )

        if not pro:  # Apply primary color directly if not in pro mode
            fig.update_traces(line_color=primary_color)

        # Add percentage markers for market share mode
        if pro and pro_mode == 'market_share':
            fig.update_traces(
                mode='lines+markers+text',
                text=trends_pd['Price'].round(1).astype(str) + '%',
                textposition='top center'
            )
            fig.update_layout(yaxis_title='Price Difference (%)')
        else:
            fig.update_layout(yaxis_title='Average Price')

        # Update layout
        fig.update_layout(
            margin=dict(l=2, r=2, t=5, b=2),
            xaxis_title='Model Year',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        # Update legend labels for temporal comparison mode
        if pro and pro_mode == 'temporal_comparison':
            current_label = filter_data.get(
                '_temporal_current_label', 'Current Period')
            previous_label = filter_data.get(
                '_temporal_previous_label', 'Previous Period')

            # Update legend labels to show smart time period labels
            for trace in fig.data:
                if trace.name == 'Current Period':
                    trace.name = current_label
                elif trace.name == 'Previous Period':
                    trace.name = previous_label

        self._apply_global_layout(fig)

        if pro and pro_mode == 'market_share':
            title = f'Model Year Price Comparison (% Difference from Market)'
        else:
            title = f'Model Year Price Averages'

        return fig, title

    def get_enum_values(self, group):
        if group == 'ModelYearRanges':
            return year_ranges_enum
        elif group == 'PriceBracket':
            return price_ranges_enum
        else:
            return None

    def dual_group_pivot(self, filter_data, group_1, group_2):
        data, top_n = self.filter_data(filter_data)
        pro = filter_data.get('pro', False)
        temporal_comparison = filter_data.get(
            'pro_mode', 'benchmark') == 'temporal_comparison'
        print(temporal_comparison)

        if temporal_comparison:
            segment_1 = 'Previous Period'
            segment_2 = 'Current Period'
        else:
            segment_1 = 'Market'
            segment_2 = filter_data.get('target_company')
        print('Inside dual_group_pivot')
        print(segment_1, segment_2)

        if pro:
            dfs = [
                data.filter(pl.col('segment') == segment_1),
                data.filter(pl.col('segment') == segment_2)
            ]
            num_cols = 2
            subplot_titles = [f'{segment_1}',
                              f'{segment_2}']
        else:
            dfs = [data]
            num_cols = 1
            subplot_titles = ['']

        fig = make_subplots(rows=1, cols=num_cols,
                            shared_yaxes=True, subplot_titles=subplot_titles)

        if filter_data.get('make'):
            top_values = filter_data['make']
        else:
            # top_values = data[group_1].value_counts().head(
            #     top_n).index.tolist()
            top_values = data.group_by(
                pl.col(group_1)
            ).agg(
                pl.col(group_1).count().alias('count')
            ).sort(
                by='count', descending=True
            ).select(
                pl.col(group_1)
            ).limit(top_n)

        for i, df in enumerate(dfs, start=1):
            grouping = (
                df.join(top_values, on=group_1, how='inner')
                .select(
                    pl.col(group_1).cast(pl.Categorical),
                    pl.col(group_2).cast(self.get_enum_values(group_2))
                )
                .group_by(
                    pl.col(group_1),
                    pl.col(group_2)
                )
                .agg(
                    pl.len().alias('count')
                )
            )
            pivot = (
                grouping
                .collect()
                .sort(by=group_2)
                .pivot(
                    index=group_1,
                    on=group_2,
                    values='count',
                )
                .lazy()
            )
            pivot = pivot.collect().to_pandas()
            pivot = pivot.set_index(group_1)
            pivot.fillna(0, inplace=True)
            pivot = pivot.div(pivot.sum(axis=1), axis=0)
            pivot = pivot.round(2) * 100
            # pivot = pivot.reset_index()

            heatmap = go.Heatmap(
                z=pivot.values,
                x=pivot.columns,
                y=pivot.index,
                text=pivot.values,
                texttemplate='%{text:.1f}%',
                textfont={'size': 10},
                colorscale='Blues',
                showscale=False if i > 1 else True
            )

            fig.add_trace(heatmap, row=1, col=i)

            fig.update_xaxes(side='bottom', row=1, col=i)
            fig.update_yaxes(
                title_text='', showticklabels=True if i == 1 else False, row=1, col=i)
            fig.update_xaxes(title_text='', showticklabels=True, row=1, col=i)

        fig.update_layout(margin=dict(l=2, r=2, t=35, b=2))
        self._apply_global_layout(fig)
        title = f'{group_2} Distribution by Top {top_n} {group_1}s'
        return fig, title

    def make_model_year_pivot(self, filter_data):
        data, top_n = self.filter_data(filter_data)
        if filter_data['make']:
            top_makes = filter_data['make']
        else:
            top_makes = data['Make'].value_counts().head(top_n).index.tolist()

        data = data[data['Make'].isin(top_makes)]
        pivot = data.pivot_table(
            index='Make', columns='ModelYearRanges', values=self.date_col, aggfunc='count')
        pivot.fillna(0, inplace=True)
        pivot = pivot.div(pivot.sum(axis=1), axis=0)
        # round to 2 decimal places
        pivot = pivot.round(2)
        pivot = pivot * 100
        fig = px.imshow(pivot, aspect='auto', text_auto=True,
                        color_continuous_scale='Blues')
        fig.update_xaxes(side='top')
        fig.update_layout(margin=dict(l=2, r=2, t=5, b=2))
        self._apply_global_layout(fig)
        title = f'Model Year Distribution by Top {top_n} Makes'
        return fig, title

    def make_country_choropleth(self, filter_data):
        data, top_n = self.filter_data(filter_data)
        country_counts = data.group_by(
            pl.col('Country').cast(pl.Categorical)
        ).agg(
            pl.len().alias('Count')
        ).sort(
            by='Count', descending=True
        )
        country_counts = country_counts.with_columns(
            pl.col('Country').cast(pl.String),
            (pl.col('Count') / pl.col('Count').sum()
             * 100).alias('normalized_count')
        )
        country_counts = country_counts.collect().to_pandas()
        country_counts['iso'] = country_counts['Country'].map(country_iso)
        country_counts['normalized_count'] = country_counts['normalized_count'].round(2)

        # Create choropleth using go.Choropleth for better control over missing countries
        fig = go.Figure(data=go.Choropleth(
            locations=country_counts['iso'],
            z=country_counts['normalized_count'],
            text=country_counts['Country'],
            colorscale='Greens',
            autocolorscale=False,
            marker_line_color='rgb(200, 200, 200)',
            marker_line_width=0.5,
            colorbar_title="Percentage"
        ))
        
        fig.update_layout(
            margin=dict(l=2, r=2, t=5, b=2),
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='equirectangular',
                showland=True,
                landcolor='lightblue',  # Set light blue color for countries with no data
                showocean=True,
                oceancolor='rgba(76, 201, 240, 0.2)',
                showcountries=True,
                countrycolor='rgb(200, 200, 200)',
                coastlinecolor='rgb(200, 200, 200)',
                projection_scale=1.1
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        # Note: Countries without data will appear in the landcolor (light blue)

        self._apply_global_layout(fig)

        title = f'Distribution by Top {top_n} Vehicle Manufacturing Countries'
        return fig, title

    def ev_composition_pie(self, filter_data):
        # Create a copy to avoid modifying the original filter_data
        modified_filter_data = filter_data.copy()
        modified_filter_data['is_ev'] = False
        data, top_n = self.filter_data(modified_filter_data)

        ev_comp = data.group_by(
            pl.col('IsEV').cast(pl.Boolean)
        ).agg(
            pl.len().alias('count')
        ).sort(
            by='count', descending=True
        )
        ev_comp = ev_comp.collect().to_pandas()
        ev_comp['IsEV'] = ev_comp['IsEV'].map({True: 'EV', False: 'Non-EV'})
        labels = ev_comp['IsEV'].tolist()
        values = ev_comp['count'].tolist()

        fig = go.Figure(
            data=go.Pie(labels=labels, values=values, pull=[0.2, 0])
        )
        fig.update_layout(margin=dict(l=2, r=2, t=5, b=2))
        self._apply_global_layout(fig)
        title = f'EV Composition'
        return fig, title

    def ev_trends(self, filter_data, rolling_window=7):
        data_pl, _ = self.filter_data(filter_data)  # Polars DataFrame

        # if data_pl.is_empty():
        #     fig = go.Figure()
        #     title_str = f'Normalized EV Inquiry Trends ({rolling_window}-Day Rolling Average) - No Input Data'
        #     self._apply_global_layout(fig)
        #     fig.update_layout(
        #         margin=dict(l=2, r=2, t=5, b=2),
        #         xaxis_title='', yaxis_title='',
        #         # Optional: add an annotation if you want a message directly on the plot
        #         # annotations=[dict(text="No input data available", xref="paper", yref="paper",
        #         #                   x=0.5, y=0.5, showarrow=False, font=dict(size=16))]
        #     )
        #     return fig, title_str

        # Proceed with Polars operations
        # Date column is already a datetime type from filter_data method
        # Convert to date for daily grouping
        daily_counts_lazy = (
            data_pl.select(
                pl.col(self.date_col).dt.date()
            )
            # Ensure sorted for group_by_dynamic, though it sorts its output
            .sort(self.date_col)
            .group_by_dynamic(
                index_column=self.date_col,
                every="1d",
            )
            .agg(
                pl.len().alias('daily_inquiries')  # pl.len() counts rows in group
            )
        )

        daily_counts_collected = daily_counts_lazy

        if False:
            # No daily data points after grouping (e.g., very small date range in input)
            daily_counts_pd = pd.DataFrame(
                columns=[self.date_col, 'normalized_rolling_avg'])
            title_str = f'Normalized EV Inquiry Trends ({rolling_window}-Day Rolling Average) - No Daily Data'
        else:
            # Continue with the collected DataFrame, making it lazy again for chained operations
            daily_counts_pl = daily_counts_collected.with_columns(
                pl.col('daily_inquiries')
                .rolling_mean(window_size=rolling_window, min_periods=1)
                .alias(f'{rolling_window}_day_rolling_avg'),
            )

            # Calculate max_rolling_avg. Collect is needed here for the scalar.
            max_rolling_avg_df = daily_counts_pl.select(
                pl.max(f'{rolling_window}_day_rolling_avg').alias("max_val")
            )

            max_rolling_avg = None
            # if not max_rolling_avg_df.is_empty():  # Ensure the result of select max is not empty
            # print(max_rolling_avg_df.collect_schema())
            max_rolling_avg = max_rolling_avg_df.collect()
            max_rolling_avg = max_rolling_avg['max_val'].item()

            if max_rolling_avg is not None and max_rolling_avg > 0:
                daily_counts_pl = daily_counts_pl.with_columns(
                    (pl.col(f'{rolling_window}_day_rolling_avg') /
                     max_rolling_avg * 100)
                    .alias('normalized_rolling_avg')
                )
            else:
                daily_counts_pl = daily_counts_pl.with_columns(
                    pl.lit(0.0).cast(pl.Float64).alias(
                        'normalized_rolling_avg')
                )

            daily_counts_pd = daily_counts_pl.collect().to_pandas()
            title_str = f'Normalized EV Inquiry Trends ({rolling_window}-Day Rolling Average)'

        # Plotting
        fig = px.line(daily_counts_pd, x=self.date_col,
                      y='normalized_rolling_avg')

        fig.update_layout(margin=dict(l=2, r=2, t=5, b=2))
        fig.update_xaxes(title_text='')
        fig.update_yaxes(title_text='')

        self._apply_global_layout(fig)
        return fig, title_str

    def ev_make_date_trends(self, filter_data):
        data, top_n = self.filter_data(filter_data)
        data[self.date_col] = pd.to_datetime(
            data[self.date_col], errors='coerce')
        trends = data.groupby(['Make', self.date_col]
                              ).size().reset_index(name='count')
        pivot = trends.pivot_table(
            index=self.date_col, columns='Make', values='count')
        pivot.fillna(0, inplace=True)
        pivot_row_norm = pivot.div(pivot.sum(axis=1), axis=0)
        pivot_row_norm = pivot_row_norm * 100
        fig = px.line(
            pivot_row_norm,
            facet_row='Make',
            facet_row_spacing=0.05,
        )
        fig.update_yaxes(visible=False, fixedrange=True)
        fig.update_xaxes(title_text='')  # Remove x-axis title

        # remove facet/subplot labels
        fig.update_layout(annotations=[], overwrite=True)

        fig.update_layout(margin=dict(l=2, r=2, t=5, b=2))
        self._apply_global_layout(fig)
        title = f'EV Trends by Make'
        return fig, title

    def forecast_analysis(self, filter_data, grouping_column='Make'):
        data_pl, _ = self.filter_data(filter_data)

        # Get min and max dates - data_pl already has date column as datetime
        min_date = data_pl.select(
            pl.col(self.date_col).min()
        ).collect().item()
        max_date = data_pl.select(
            pl.col(self.date_col).max()
        ).collect().item()

        days_diff = (max_date - min_date).days
        interval = round(0.6 * days_diff)
        interval_date = min_date + timedelta(days=interval)

        # Create interval column and perform aggregations in one lazy operation
        analysis_pl = (
            data_pl.lazy()
            .with_columns(
                pl.col(grouping_column).cast(pl.String).cast(pl.Categorical)
            )
            .with_columns(
                pl.when(pl.col(self.date_col) >= interval_date)
                .then(pl.lit('current'))
                .otherwise(pl.lit('last'))
                .alias('interval')
            )
            # Get total counts per interval for normalization
            .with_columns(
                pl.col('interval')
                .count()
                .over('interval')
                .alias('interval_total')
            )
            # Get counts per grouping_column and interval
            .group_by([grouping_column, 'interval'])
            .agg(
                count=pl.len(),
                total=pl.col('interval_total').first()
            )
            .with_columns(
                percentage=(pl.col('count') / pl.col('total')
                            ).alias('percentage')
            )
            # Pivot the data
            .collect()
            .pivot(
                index=grouping_column,
                columns='interval',
                values='percentage'
            )
            .lazy()
            # Calculate change
            .with_columns(
                change=((pl.col('current') - pl.col('last')) / pl.col('current'))
            )
        )

        # Split into gainers and losers at the last possible moment
        gainers = (
            analysis_pl
            .filter(pl.col('change') > 0)
            .sort('current', descending=True)
            .collect()
            .to_pandas()
        )

        losers = (
            analysis_pl
            .filter(pl.col('change') < 0)
            .sort('current', descending=True)
            .collect()
            .to_pandas()
        )

        return gainers, losers, interval_date

    def forecast_analysis_datatables(
            self,
            filter_data,
            grouping_column='Make',
            gainer_row=None,
            loser_row=None
    ):
        gainers, losers, interval = self.forecast_analysis(
            filter_data, grouping_column)

        columns = [
            {'name': grouping_column, 'id': grouping_column},
            {'name': 'Last', 'id': 'last', 'type': 'numeric', 'format': pct_format},
            {'name': 'Current', 'id': 'current',
                'type': 'numeric', 'format': pct_format},
            {'name': 'Change', 'id': 'change',
                'type': 'numeric', 'format': pct_format}
        ]

        header_style = {
            'backgroundColor': 'rgb(0, 0, 0)',
            'color': 'rgb(255, 255, 255)',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'border': '1px solid #ddd'
        }

        gainers_data = gainers.to_dict(orient='records')
        losers_data = losers.to_dict(orient='records')

        gainers_table = DataTable(
            id='forecast-analysis-gainers-table',
            columns=columns,
            data=gainers_data,
            page_size=5,
            page_current=0,
            page_action='native',
            sort_action='native',
            column_selectable=False,
            row_selectable='single',
            cell_selectable=False,
            style_header=header_style,
            style_data_conditional=[
                {
                    'if': {'column_id': 'change'},
                    'backgroundColor': 'honeydew',
                    'color': 'forestgreen'
                }
            ]
        )

        losers_table = DataTable(
            id='forecast-analysis-losers-table',
            columns=columns,
            data=losers_data,
            page_size=5,
            page_current=0,
            page_action='native',
            sort_action='native',
            column_selectable=False,
            row_selectable='single',
            cell_selectable=False,
            style_header=header_style,
            style_data_conditional=[
                {
                    'if': {'column_id': 'change'},
                    'backgroundColor': 'mistyrose',
                    'color': 'red'
                }
            ]
        )

        return gainers_table, losers_table, gainers_data[gainer_row] if gainer_row is not None else None, losers_data[loser_row] if loser_row is not None else None, interval

    def forecast_analysis_trends(self, filter_data, grouping_column, grouping_value, interval=None, window=7):
        data_pl, _ = self.filter_data(filter_data)

        # Filter and prepare data in one lazy operation
        trends_pl = (
            data_pl.lazy()
            .filter(pl.col(grouping_column) == grouping_value)
            # .with_columns(
            #     pl.col(self.date_col).str.to_datetime('%Y-%m-%d %H:%M:%S')
            # )
            .sort(self.date_col)
            # Group by date and count occurrences
            .group_by_dynamic(
                index_column=self.date_col,
                every='1d'
            )
            .agg(
                count=pl.len()
            )
            .with_columns([
                # Calculate moving average first
                pl.col('count').rolling_mean(
                    window_size=window,
                    min_periods=1
                ).alias('trend'),
                # Store original count for reference
                pl.col('count').alias('original_count')
            ])
            .with_columns([
                # Normalize both count and trend by the maximum of original count
                (pl.col('original_count') /
                 pl.col('original_count').max() * 100).alias('count'),
                (pl.col('trend') / pl.col('original_count').max() * 100).alias('trend')
            ])
            # Only keep needed columns
            .select([self.date_col, 'count', 'trend'])
        )

        # Collect data only once for plotting
        trends_pd = trends_pl.collect().to_pandas()

        # Create the base figure with the original line
        fig = px.line(trends_pd, x=self.date_col, y='count')

        # Add moving average trend line
        fig.add_scatter(
            x=trends_pd[self.date_col],
            y=trends_pd['trend'],
            mode='lines',
            name=f'{window}-day Moving Average',
            line=dict(color='orange', width=3)
        )

        # Update layout
        fig.update_layout(
            margin=dict(l=2, r=2, t=5, b=2),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        if interval is not None:
            fig.add_vline(x=interval, line_dash='dash', line_color='red')

        self._apply_global_layout(fig)

        title = f'Forecast Analysis Trends for {grouping_column}: {grouping_value}'
        return fig, title

    # === PLOTLY INDICATOR METHODS ===
    
    def ev_percentage_indicator(self, filter_data):
        """Calculate EV percentage indicator"""
        data_pl, _ = self.filter_data(filter_data)
        
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
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=ev_percentage,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "EV Percentage"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#2E8B57"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 100], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            height=300
        )
        self._apply_global_layout(fig)
        
        return fig, f"EV Percentage: {ev_percentage:.1f}%"

    def non_ev_percentage_indicator(self, filter_data):
        """Calculate Non-EV percentage indicator"""
        data_pl, _ = self.filter_data(filter_data)
        
        # Calculate Non-EV percentage
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
        non_ev_count = ev_stats.filter(pl.col('IsEV') == False)['count'].sum() if len(ev_stats.filter(pl.col('IsEV') == False)) > 0 else 0
        non_ev_percentage = (non_ev_count / total_count * 100) if total_count > 0 else 0
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=non_ev_percentage,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Non-EV Percentage"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#4169E1"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 100], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            height=300
        )
        self._apply_global_layout(fig)
        
        return fig, f"Non-EV Percentage: {non_ev_percentage:.1f}%"

    def top_make_indicator(self, filter_data):
        """Calculate top make indicator"""
        data_pl, _ = self.filter_data(filter_data)
        
        # Find top make
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
        
        if len(top_make_stats) > 0:
            top_make = top_make_stats['Make'][0]
            top_make_count = top_make_stats['count'][0]
            total_count = data_pl.select(pl.len()).collect().item()
            top_make_percentage = (top_make_count / total_count * 100) if total_count > 0 else 0
        else:
            top_make = "No Data"
            top_make_count = 0
            top_make_percentage = 0
        
        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=top_make_percentage,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Top Make: {top_make}"},
            delta={'reference': 20, 'suffix': '%'},
            number={'suffix': '%', 'font': {'size': 48}}
        ))
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            height=300
        )
        self._apply_global_layout(fig)
        
        return fig, f"Top Make: {top_make} ({top_make_percentage:.1f}%)"

    def top_manufacturing_country_indicator(self, filter_data):
        """Calculate top manufacturing country indicator"""
        data_pl, _ = self.filter_data(filter_data)
        
        # Find top manufacturing country
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
        
        if len(top_country_stats) > 0:
            top_country = top_country_stats['Country'][0]
            top_country_count = top_country_stats['count'][0]
            total_count = data_pl.select(pl.len()).collect().item()
            top_country_percentage = (top_country_count / total_count * 100) if total_count > 0 else 0
        else:
            top_country = "No Data"
            top_country_count = 0
            top_country_percentage = 0
        
        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=top_country_percentage,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Top Manufacturing Country: {top_country}"},
            delta={'reference': 30, 'suffix': '%'},
            number={'suffix': '%', 'font': {'size': 48}}
        ))
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            height=300
        )
        self._apply_global_layout(fig)
        
        return fig, f"Top Country: {top_country} ({top_country_percentage:.1f}%)"

    def total_cars_indicator(self, filter_data):
        """Calculate total number of cars indicator"""
        data_pl, _ = self.filter_data(filter_data)
        
        # Calculate total count
        total_count = data_pl.select(pl.len()).collect().item()
        
        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=total_count,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Total Number of Cars"},
            delta={'reference': 1000},
            number={'font': {'size': 48}}
        ))
        
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            height=300
        )
        self._apply_global_layout(fig)
        
        return fig, f"Total Cars: {total_count:,}"
    
    def create_all_indicators(self, filter_data):
        """Create all indicators at once for dashboard layout"""
        indicators = {}
        
        # Generate all indicators
        indicators['ev_percentage'] = self.ev_percentage_indicator(filter_data)
        indicators['non_ev_percentage'] = self.non_ev_percentage_indicator(filter_data)
        indicators['top_make'] = self.top_make_indicator(filter_data)
        indicators['top_country'] = self.top_manufacturing_country_indicator(filter_data)
        indicators['total_cars'] = self.total_cars_indicator(filter_data)
        
        return indicators


# Create separate factory instances for each dataset
vv_viz_factory = VisualizationFactory(
    data=vv, end_date=end_date, start_date=start_date, date_col='InquiryDate')

vs_viz_factory = VisualizationFactory(
    data=vs, end_date=end_date, start_date=start_date, date_col='InquiryDate')

cmf_viz_factory = VisualizationFactory(
    data=cmf, end_date=end_date, start_date=start_date, date_col='AccidentDate')

# Keep original for backward compatibility (defaults to vv data)
viz_factory = vv_viz_factory
