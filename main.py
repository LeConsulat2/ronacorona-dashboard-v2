import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Corona Dashboard",  # Title displayed in the browser tab
    page_icon="",  # Page icon (if any)
    layout="wide",  # Use a wide layout (alternatively, 'centered')
    initial_sidebar_state="expanded",  # Sidebar is expanded by default
)


# Function to display a data table
def make_table(df):
    st.write("### Country Data")
    st.dataframe(df)


# Load the statuses we are tracking: confirmed, deaths, and recovered
# Similar to a traffic light: red for confirmed, black for deaths, and green for recovered
conditions = ["confirmed", "deaths", "recovered"]

# Load the daily report data – think of it as today's dashboard snapshot
daily_df = pd.read_csv("data/daily_report.csv")

# Calculate global totals – a summary of the worldwide situation
# Like the final tally in a bank ledger where all numbers are summed up
totals_df = (
    daily_df[["Confirmed", "Deaths", "Recovered"]].sum().reset_index(name="count")
)
totals_df = totals_df.rename(columns={"index": "condition"})

# Organize data by country
# Similar to arranging report cards for each class, we summarize the situation per country
countries_df = daily_df[["Country_Region", "Confirmed", "Deaths", "Recovered"]]
countries_df = (
    countries_df.groupby("Country_Region")
    .sum()
    .sort_values(
        by="Confirmed", ascending=False
    )  # Sorted in descending order by confirmed cases
    .reset_index()
)

# Prepare a list of countries for the dropdown menu
# Sorted in alphabetical order to make selection easier
dropdown_options = countries_df.sort_values("Country_Region").reset_index()
dropdown_options = dropdown_options["Country_Region"]


def make_country_df(country):
    """
    Function to generate time series data for a specific country.
    Much like tracking a student's daily performance, it monitors a country's daily changes.
    """

    def make_df(df, condition):
        # Remove unnecessary columns and compute the daily totals
        df = df.drop(
            ["Province/State", "Country/Region", "Lat", "Long"], axis=1, errors="ignore"
        )
        df_sum = df.sum().reset_index(name=condition)
        df_sum = df_sum.rename(columns={"index": "date"})
        return df_sum

    final_df = None

    # Process data for confirmed, deaths, and recovered one at a time
    # Like assembling pieces of a puzzle, we combine the three datasets into one
    for condition in conditions:
        df = pd.read_csv(f"data/time_{condition}.csv")
        df = df.rename(
            columns={"Country/Region": "Country_Region", "Lat": "Lat", "Long": "Long_"}
        )
        df = df.loc[df["Country_Region"] == country]
        condition_df = make_df(df, condition)
        if final_df is None:
            final_df = condition_df
        else:
            final_df = final_df.merge(condition_df)

    return final_df


def make_global_df():
    """
    Function to generate global time series data.
    Similar to examining the daily performance of an entire school,
    this function provides an overview of the worldwide daily changes.
    """

    def make_df(df, condition):
        # Remove unnecessary columns and compute the daily totals
        df = df.drop(
            ["Province/State", "Country/Region", "Lat", "Long"], axis=1, errors="ignore"
        )
        df_sum = df.sum().reset_index(name=condition)
        df_sum = df_sum.rename(columns={"index": "date"})
        return df_sum

    final_df = None

    # Aggregate confirmed, deaths, and recovered data globally
    # Like compiling global weather forecasts, all data is consolidated here
    for condition in conditions:
        df = pd.read_csv(f"data/time_{condition}.csv")
        df = df.rename(
            columns={"Country/Region": "Country_Region", "Lat": "Lat", "Long": "Long_"}
        )
        condition_df = make_df(df, condition)
        if final_df is None:
            final_df = condition_df
        else:
            final_df = final_df.merge(condition_df)

    return final_df


# Title and Header for the dashboard
st.title("Corona Dashboard")

# Create a two-column layout: the first column is 3 times wider than the second
col1, col2 = st.columns([3, 1])

with col1:
    # Generate the bubble map figure
    bubble_map = px.scatter_geo(
        countries_df,
        size="Confirmed",  # Bubble size reflects confirmed cases
        projection="equirectangular",
        color="Confirmed",  # Bubble color reflects confirmed cases
        locations="Country_Region",  # Map the country names to their locations
        locationmode="country names",
        size_max=60,
        title="Confirmed By Country",
        template="plotly_dark",
        color_continuous_scale=px.colors.sequential.Oryel,
        hover_data={
            "COnfirmed": ":,",
            "Deaths": ":,",
            "Recovered": ":,",
            "Country_Region": False,
        },
    )

    bubble_map.update_layout(
        margin=dict(l=0, r=0, t=50, b=0), coloraxis_colorbar=dict(xanchor="left", x=0)
    )

    # Render the bubble map
    st.plotly_chart(bubble_map, use_container_width=True)

    with col2:
        # Render the data table
        make_table(countries_df)

    # Second row: Create a new set of columns, with a 1:3 ratio
    col3, col4 = st.columns([1, 3])

    with col3:
        # Generate the bar graph figure for global totals
        bars_graph = px.bar(
            totals_df,
            x="condition",
            hover_data={"count": ":,"},
            y="count",
            template="plotly_dark",
            title="Total Global Cases",
            labels={"condition": "Condition", "count": "Count", "color": "Condition"},
        )

        bars_graph.update_traces(marker_color=["#e74c3c", "#8e44ad", "#27ae60"])

        # Render the bar graph
        st.plotly_chart(bars_graph, use_container_width=True)

    with col4:
        # Dropdown menu for country selection
        country = st.selectbox("Select a Country:", options=dropdown_options)

        # Update the country graph based on the selected country
        if country:
            df = make_country_df(country)
        else:
            df = make_global_df()

        fig = px.line(
            df,
            x="date",
            y=["confirmed", "deaths", "recovered"],
            template="plotly_dark",
            labels={"value": "Cases", "variable": "Condition", "date": "Date"},
            hover_date={"value": ":,", "variable": False, "date": False},
        )

        fig.update_xaxes(rangeslider_visible=True)
        # Set custom line colors for each status
        fig["data"][0]["line"]["color"] = "#e74c3c"
        fig["data"][1]["line"]["color"] = "#8e44ad"
        fig["data"][2]["line"]["color"] = "#27ae60"

        # Render the line graph
        st.plotly_chart(fig, use_container_width=True)
