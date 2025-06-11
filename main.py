import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration: Establish the dashboard’s overall appearance and behavior.
st.set_page_config(
    page_title="Corona Dashboard",  # Title that appears in the browser tab.
    page_icon="",  # Optional icon for the page.
    layout="wide",  # Use a wide layout for a more expansive presentation.
    initial_sidebar_state="expanded",  # The sidebar is expanded by default.
)


# Function to render a data table on the dashboard.
def make_table(df):
    st.write("### Country Data")
    st.dataframe(df)


# Load the three statuses we aim to track: confirmed, deaths, and recovered.
# Think of it as a traffic light system: each status is as distinct as a different color.
conditions = ["confirmed", "deaths", "recovered"]

# Load the daily report dataset – consider this as today’s snapshot of the global situation.
daily_df = pd.read_csv("data/daily_report.csv")

# Compute global totals to present a succinct summary of worldwide figures.
# This is akin to the final tally in an account ledger, where individual numbers are summed comprehensively.
totals_df = (
    daily_df[["Confirmed", "Deaths", "Recovered"]].sum().reset_index(name="count")
)
totals_df = totals_df.rename(columns={"index": "condition"})

# Aggregate the data by country.
# Much like compiling report cards for various classes, this organizes each nation's data succinctly.
countries_df = daily_df[["Country_Region", "Confirmed", "Deaths", "Recovered"]]
countries_df = (
    countries_df.groupby("Country_Region")
    .sum()
    .sort_values(
        by="Confirmed", ascending=False
    )  # Sort nations in descending order by confirmed cases.
    .reset_index()
)

# Prepare a sorted list of countries for the dropdown menu.
# The list is sorted alphabetically to facilitate effortless selection.
dropdown_options = countries_df.sort_values("Country_Region").reset_index()
dropdown_options = dropdown_options["Country_Region"]


def make_country_df(country):
    """
    Generates a time series dataset for a specified country.
    Comparable to monitoring a student’s daily performance, this function tracks
    the changes in confirmed cases, deaths, and recovered counts over time for the chosen country.
    """

    def make_df(df, condition):
        # Remove unnecessary columns and compute daily totals.
        df = df.drop(
            ["Province/State", "Country/Region", "Lat", "Long"], axis=1, errors="ignore"
        )
        df_sum = df.sum().reset_index(name=condition)
        df_sum = df_sum.rename(columns={"index": "date"})
        return df_sum

    final_df = None

    # Process each status individually (confirmed, deaths, recovered),
    # and then merge the resulting datasets into a cohesive time series.
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
    Generates a global time series dataset.
    This function consolidates worldwide data to provide an aggregate view
    of daily changes, much like reviewing the collective performance of an entire school.
    """

    def make_df(df, condition):
        # Remove non-essential columns and calculate the daily sums.
        df = df.drop(
            ["Province/State", "Country/Region", "Lat", "Long"], axis=1, errors="ignore"
        )
        df_sum = df.sum().reset_index(name=condition)
        df_sum = df_sum.rename(columns={"index": "date"})
        return df_sum

    final_df = None

    # Assemble global data for confirmed cases, deaths, and recoveries.
    # Similar to compiling a worldwide weather forecast, this merges all data into a unified dataset.
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


# Dashboard Title and Header
st.title("Corona Dashboard")

# Create a two-column layout: the left column is three times wider than the right.
col1, col2 = st.columns([3, 1])

with col1:
    # Build the bubble map using geographical data.
    bubble_map = px.scatter_geo(
        countries_df,
        size="Confirmed",  # The bubble's size represents the number of confirmed cases.
        projection="equirectangular",
        color="Confirmed",  # The bubble's hue also reflects confirmed cases.
        locations="Country_Region",  # Associate country names with their geographic locations.
        locationmode="country names",
        size_max=60,
        title="Confirmed By Country",
        template="plotly_dark",
        color_continuous_scale=px.colors.sequential.Oryel,
        hover_data={
            "Confirmed": ":,",
            "Deaths": ":,",
            "Recovered": ":,",
            "Country_Region": False,
        },
    )

    # Adjust layout margins and the color bar for optimal display.
    bubble_map.update_layout(
        margin=dict(l=0, r=0, t=50, b=0), coloraxis_colorbar=dict(xanchor="left", x=0)
    )

    # Render the bubble map within the left column.
    st.plotly_chart(bubble_map, use_container_width=True)

with col2:
    # Render the data table within the right column.
    make_table(countries_df)

# Create a second row with two columns arranged in a 1:3 ratio.
col3, col4 = st.columns([1, 3])

with col3:
    # Build a bar graph to represent the calculated global totals.
    bars_graph = px.bar(
        totals_df,
        x="condition",
        hover_data={"count": ":,"},
        y="count",
        template="plotly_dark",
        title="Total Global Cases",
        labels={"condition": "Condition", "count": "Count", "color": "Condition"},
    )

    # Customize the color of the bars for clarity.
    bars_graph.update_traces(marker_color=["#e74c3c", "#8e44ad", "#27ae60"])

    # Render the bar graph in the left column of the second row.
    st.plotly_chart(bars_graph, use_container_width=True)

with col4:
    # Create a dropdown menu to enable country selection.
    country = st.selectbox("Select a Country:", options=dropdown_options)

    # Update the time series dataset based on the selected country.
    if country:
        df = make_country_df(country)
    else:
        df = make_global_df()

    # Build a line chart to illustrate trends over time.
    fig = px.line(
        df,
        x="date",
        y=["confirmed", "deaths", "recovered"],
        template="plotly_dark",
        labels={"value": "Cases", "variable": "Condition", "date": "Date"},
        hover_data={"value": ":,", "variable": False, "date": False},
    )

    # Enable a range slider on the x-axis for easier navigation of the timeline.
    fig.update_xaxes(rangeslider_visible=True)

    # Customize the line colors to clearly distinguish each status.
    fig["data"][0]["line"]["color"] = "#e74c3c"
    fig["data"][1]["line"]["color"] = "#8e44ad"
    fig["data"][2]["line"]["color"] = "#27ae60"

    # Render the line chart within the right column of the second row.
    st.plotly_chart(fig, use_container_width=True)
