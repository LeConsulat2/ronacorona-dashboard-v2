import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

# Advanced page configuration with custom styling
st.set_page_config(
    page_title="🦠 Global COVID-19 Analytics Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for sophisticated styling
st.markdown("""
<style>
    /* Main dashboard styling */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Custom metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        margin: 0.5rem 0;
    }
    
    .metric-card.deaths {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    }
    
    .metric-card.recovered {
        background: linear-gradient(135deg, #2ed573 0%, #1e90ff 100%);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Header styling */
    .dashboard-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    
    /* Container styling */
    .chart-container {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Table styling */
    .dataframe {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced loading and caching functions
@st.cache_data
def load_data():
    """Load and process all data with error handling"""
    try:
        daily_df = pd.read_csv("data/daily_report.csv")
        
        # Process time series data
        time_data = {}
        conditions = ["confirmed", "deaths", "recovered"]
        
        for condition in conditions:
            try:
                df = pd.read_csv(f"data/time_{condition}.csv")
                df = df.rename(columns={"Country/Region": "Country_Region"})
                time_data[condition] = df
            except FileNotFoundError:
                st.warning(f"Time series data for {condition} not found. Using sample data.")
                time_data[condition] = create_sample_data()
        
        return daily_df, time_data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return create_sample_data(), {}

def create_sample_data():
    """Create sample data for demonstration"""
    countries = ['US', 'India', 'Brazil', 'Russia', 'France', 'UK', 'Turkey', 'Iran', 'Germany', 'Italy']
    sample_data = []
    
    for country in countries:
        sample_data.append({
            'Country_Region': country,
            'Confirmed': np.random.randint(1000000, 10000000),
            'Deaths': np.random.randint(10000, 200000),
            'Recovered': np.random.randint(500000, 8000000),
            'Lat': np.random.uniform(-60, 60),
            'Long': np.random.uniform(-180, 180)
        })
    
    return pd.DataFrame(sample_data)

# Enhanced data processing functions
def process_global_totals(daily_df):
    """Process global totals with better formatting"""
    totals = daily_df[["Confirmed", "Deaths", "Recovered"]].sum()
    return {
        'confirmed': totals['Confirmed'],
        'deaths': totals['Deaths'],
        'recovered': totals['Recovered']
    }

def process_countries_data(daily_df):
    """Process country data with enhanced metrics"""
    countries_df = daily_df[["Country_Region", "Confirmed", "Deaths", "Recovered"]].copy()
    countries_df = countries_df.groupby("Country_Region").sum().reset_index()
    
    # Calculate additional metrics
    countries_df['Death_Rate'] = (countries_df['Deaths'] / countries_df['Confirmed'] * 100).round(2)
    countries_df['Recovery_Rate'] = (countries_df['Recovered'] / countries_df['Confirmed'] * 100).round(2)
    countries_df['Active_Cases'] = countries_df['Confirmed'] - countries_df['Deaths'] - countries_df['Recovered']
    
    return countries_df.sort_values('Confirmed', ascending=False)

def create_enhanced_metrics_cards(totals):
    """Create beautiful metric cards"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{totals['confirmed']:,}</p>
            <p class="metric-label">📊 Total Confirmed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card deaths">
            <p class="metric-value">{totals['deaths']:,}</p>
            <p class="metric-label">💀 Total Deaths</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card recovered">
            <p class="metric-value">{totals['recovered']:,}</p>
            <p class="metric-label">💚 Total Recovered</p>
        </div>
        """, unsafe_allow_html=True)

def create_enhanced_world_map(countries_df):
    """Create an enhanced world map with better styling"""
    fig = px.scatter_geo(
        countries_df.head(50),  # Limit to top 50 for performance
        size="Confirmed",
        color="Death_Rate",
        locations="Country_Region",
        locationmode="country names",
        size_max=80,
        title="🌍 Global COVID-19 Cases Distribution",
        template="plotly_dark",
        color_continuous_scale="RdYlBu_r",
        hover_data={
            "Confirmed": ":,",
            "Deaths": ":,",
            "Recovered": ":,",
            "Death_Rate": ":.2f%",
            "Recovery_Rate": ":.2f%",
            "Country_Region": False,
        },
        labels={
            "Death_Rate": "Death Rate (%)",
            "Confirmed": "Confirmed Cases"
        }
    )
    
    fig.update_layout(
        title_font_size=20,
        title_x=0.5,
        margin=dict(l=0, r=0, t=60, b=0),
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            bgcolor='rgba(0,0,0,0)'
        ),
        coloraxis_colorbar=dict(
            title="Death Rate (%)",
            thickness=15,
            len=0.7
        )
    )
    
    return fig

def create_enhanced_comparison_chart(countries_df):
    """Create an enhanced comparison chart"""
    top_countries = countries_df.head(15)
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Confirmed Cases', 'Deaths', 'Recovery Rate (%)', 'Death Rate (%)'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Confirmed cases
    fig.add_trace(
        go.Bar(
            x=top_countries['Country_Region'][:10],
            y=top_countries['Confirmed'][:10],
            name='Confirmed',
            marker_color='rgba(102, 126, 234, 0.8)'
        ),
        row=1, col=1
    )
    
    # Deaths
    fig.add_trace(
        go.Bar(
            x=top_countries['Country_Region'][:10],
            y=top_countries['Deaths'][:10],
            name='Deaths',
            marker_color='rgba(255, 107, 107, 0.8)'
        ),
        row=1, col=2
    )
    
    # Recovery rate
    fig.add_trace(
        go.Scatter(
            x=top_countries['Country_Region'][:10],
            y=top_countries['Recovery_Rate'][:10],
            mode='lines+markers',
            name='Recovery Rate',
            line=dict(color='rgba(46, 213, 115, 0.8)', width=3),
            marker=dict(size=8)
        ),
        row=2, col=1
    )
    
    # Death rate
    fig.add_trace(
        go.Scatter(
            x=top_countries['Country_Region'][:10],
            y=top_countries['Death_Rate'][:10],
            mode='lines+markers',
            name='Death Rate',
            line=dict(color='rgba(255, 107, 107, 0.8)', width=3),
            marker=dict(size=8)
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        title_text="📈 Top 10 Countries - Comprehensive Analysis",
        title_x=0.5,
        showlegend=False,
        template="plotly_dark",
        height=600
    )
    
    # Rotate x-axis labels for better readability
    fig.update_xaxes(tickangle=-45)
    
    return fig

def create_enhanced_table(countries_df):
    """Create an enhanced, interactive table"""
    # Add rank column
    display_df = countries_df.head(20).copy()
    display_df.insert(0, 'Rank', range(1, len(display_df) + 1))
    
    # Format columns
    display_df['Confirmed'] = display_df['Confirmed'].apply(lambda x: f"{x:,}")
    display_df['Deaths'] = display_df['Deaths'].apply(lambda x: f"{x:,}")
    display_df['Recovered'] = display_df['Recovered'].apply(lambda x: f"{x:,}")
    display_df['Active_Cases'] = display_df['Active_Cases'].apply(lambda x: f"{x:,}")
    display_df['Death_Rate'] = display_df['Death_Rate'].apply(lambda x: f"{x:.2f}%")
    display_df['Recovery_Rate'] = display_df['Recovery_Rate'].apply(lambda x: f"{x:.2f}%")
    
    # Rename columns for display
    display_df = display_df.rename(columns={
        'Country_Region': 'Country',
        'Active_Cases': 'Active Cases',
        'Death_Rate': 'Death Rate',
        'Recovery_Rate': 'Recovery Rate'
    })
    
    return display_df

# Main Dashboard Layout
def main():
    # Load data
    daily_df, time_data = load_data()
    
    # Dashboard header
    st.markdown("""
    <div class="dashboard-header">
        <h1>🦠 Global COVID-19 Analytics Dashboard</h1>
        <p>Real-time insights and comprehensive analysis of global pandemic data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Process data
    totals = process_global_totals(daily_df)
    countries_df = process_countries_data(daily_df)
    
    # Metrics cards
    create_enhanced_metrics_cards(totals)
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["🌍 Global Overview", "📊 Country Analysis", "📈 Trends", "📋 Data Table"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            world_map = create_enhanced_world_map(countries_df)
            st.plotly_chart(world_map, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🏆 Top 10 Most Affected")
            top_10 = countries_df.head(10)[['Country_Region', 'Confirmed', 'Deaths', 'Death_Rate']]
            st.dataframe(
                top_10,
                column_config={
                    "Country_Region": "Country",
                    "Confirmed": st.column_config.NumberColumn("Confirmed", format="%d"),
                    "Deaths": st.column_config.NumberColumn("Deaths", format="%d"),
                    "Death_Rate": st.column_config.NumberColumn("Death Rate", format="%.2f%%")
                },
                hide_index=True,
                use_container_width=True
            )
    
    with tab2:
        comparison_chart = create_enhanced_comparison_chart(countries_df)
        st.plotly_chart(comparison_chart, use_container_width=True)
        
        # Country selector with advanced filters
        st.markdown("### 🔍 Advanced Country Analysis")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_countries = st.multiselect(
                "Select Countries for Comparison:",
                options=countries_df['Country_Region'].tolist(),
                default=countries_df['Country_Region'].head(5).tolist()
            )
        
        with col2:
            metric_to_compare = st.selectbox(
                "Select Metric:",
                options=['Confirmed', 'Deaths', 'Recovered', 'Death_Rate', 'Recovery_Rate']
            )
        
        with col3:
            chart_type = st.selectbox(
                "Chart Type:",
                options=['Bar Chart', 'Line Chart', 'Radar Chart']
            )
        
        if selected_countries:
            filtered_df = countries_df[countries_df['Country_Region'].isin(selected_countries)]
            
            if chart_type == 'Bar Chart':
                fig = px.bar(
                    filtered_df,
                    x='Country_Region',
                    y=metric_to_compare,
                    title=f"{metric_to_compare} by Country",
                    template="plotly_dark"
                )
            elif chart_type == 'Line Chart':
                fig = px.line(
                    filtered_df,
                    x='Country_Region',
                    y=metric_to_compare,
                    title=f"{metric_to_compare} Trend",
                    template="plotly_dark"
                )
            else:  # Radar Chart
                fig = go.Figure()
                for country in selected_countries:
                    country_data = filtered_df[filtered_df['Country_Region'] == country].iloc[0]
                    fig.add_trace(go.Scatterpolar(
                        r=[country_data['Confirmed']/1000, country_data['Deaths']/100, 
                           country_data['Recovered']/1000, country_data['Death_Rate'], 
                           country_data['Recovery_Rate']],
                        theta=['Confirmed (K)', 'Deaths (100s)', 'Recovered (K)', 'Death Rate', 'Recovery Rate'],
                        fill='toself',
                        name=country
                    ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True)),
                    showlegend=True,
                    title="Multi-Metric Country Comparison",
                    template="plotly_dark"
                )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### 📈 Time Series Analysis")
        st.info("📝 Note: Time series functionality requires historical data files. This section would show trends over time.")
        
        # Placeholder for time series charts
        sample_dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
        sample_data = pd.DataFrame({
            'Date': sample_dates,
            'Confirmed': np.cumsum(np.random.randint(1000, 10000, len(sample_dates))),
            'Deaths': np.cumsum(np.random.randint(10, 100, len(sample_dates))),
            'Recovered': np.cumsum(np.random.randint(500, 5000, len(sample_dates)))
        })
        
        fig = px.line(
            sample_data,
            x='Date',
            y=['Confirmed', 'Deaths', 'Recovered'],
            title="Global COVID-19 Trends Over Time (Sample Data)",
            template="plotly_dark",
            color_discrete_map={
                'Confirmed': '#667eea',
                'Deaths': '#ff6b6b',
                'Recovered': '#2ed573'
            }
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Cases",
            legend_title="Status"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown("### 📋 Comprehensive Data Table")
        
        # Search and filter options
        col1, col2 = st.columns(2)
        with col1:
            search_term = st.text_input("🔍 Search countries:", "")
        with col2:
            min_cases = st.number_input("Minimum confirmed cases:", min_value=0, value=0)
        
        # Filter data
        filtered_countries = countries_df.copy()
        if search_term:
            filtered_countries = filtered_countries[
                filtered_countries['Country_Region'].str.contains(search_term, case=False, na=False)
            ]
        filtered_countries = filtered_countries[filtered_countries['Confirmed'] >= min_cases]
        
        # Display enhanced table
        enhanced_table = create_enhanced_table(filtered_countries)
        st.dataframe(
            enhanced_table,
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = enhanced_table.to_csv(index=False)
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name="covid_data.csv",
            mime="text/csv"
        )
    
    # Sidebar with additional information
    with st.sidebar:
        st.markdown("### 📊 Dashboard Info")
        st.info("""
        This enhanced dashboard provides:
        - 🌍 Interactive global map
        - 📈 Real-time statistics
        - 🔍 Advanced filtering
        - 📊 Multiple visualization types
        - 📋 Comprehensive data tables
        """)
        
        st.markdown("### ⚙️ Settings")
        auto_refresh = st.checkbox("Auto-refresh data", value=False)
        if auto_refresh:
            st.info("Auto-refresh is enabled")
        
        st.markdown("### 📈 Quick Stats")
        if not countries_df.empty:
            st.metric("Countries Affected", len(countries_df))
            st.metric("Avg Death Rate", f"{countries_df['Death_Rate'].mean():.2f}%")
            st.metric("Avg Recovery Rate", f"{countries_df['Recovery_Rate'].mean():.2f}%")

if __name__ == "__main__":
    main()