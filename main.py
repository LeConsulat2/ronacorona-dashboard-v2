import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Corona Dashboard",
    page_icon="",
    layout="wide",  # 'centered' or 'wide'
    initial_sidebar_state="expanded",
)

# Embed custom CSS
st.markdown(
    """
    <style>
    .css-1aumxhk{
        height: 90vh; /* Adjust this value as needed */
    }


    """
)


# Function to display a data table
def make_table(df):
    st.write("### Country Data")
    st.dataframe(df)


# Load data
conditions = ["confirmed", "deaths", "recovered"]

daily_df = pd.read_csv("data/daily_report.csv")

totals_df = (
    daily_df[["Confirmed", "Deaths", "Recovered"]].sum().reset_index(name="count")
)
totals_df = totals_df.rename(columns={"index": "condition"})

countries_df = daily_df[["Country_Region", "Confirmed", "Deaths", "Recovered"]]
countries_df = (
    countries_df.groupby("Country_Region")
    .sum()
    .sort_values(by="Confirmed", ascending=False)
    .reset_index()
)

dropdown_options = countries_df.sort_values("Country_Region").reset_index()
dropdown_options = dropdown_options["Country_Region"]


def make_country_df(country):
    def make_df(df, condition):
        df = df.drop(
            ["Province/State", "Country/Region", "Lat", "Long"], axis=1, errors="ignore"
        )
        df_sum = df.sum().reset_index(name=condition)
        df_sum = df_sum.rename(columns={"index": "date"})
        return df_sum

    final_df = None

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
    def make_df(df, condition):
        df = df.drop(
            ["Province/State", "Country/Region", "Lat", "Long"], axis=1, errors="ignore"
        )
        df_sum = df.sum().reset_index(name=condition)
        df_sum = df_sum.rename(columns={"index": "date"})
        return df_sum

    final_df = None

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


# Title and header
st.title("Corona Dashboard")

# Create a layout with columns to align elements to the left
col1, col2 = st.columns(
    [3, 1]
)  # The first column is three times the width of the second column

with col1:
    # Create bubble map figure
    bubble_map = px.scatter_geo(
        countries_df,
        size="Confirmed",
        projection="equirectangular",
        hover_name="Country_Region",
        color="Confirmed",
        locations="Country_Region",
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
    bubble_map.update_layout(
        margin=dict(l=0, r=0, t=50, b=0), coloraxis_colorbar=dict(xanchor="left", x=0)
    )

    # Display the bubble map
    st.plotly_chart(bubble_map, use_container_width=True)

with col2:
    # Display the data table
    make_table(countries_df)

# Second row of elements
col3, col4 = st.columns([1, 3])

with col3:
    # Create bar graph figure
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

    # Display the bar graph
    st.plotly_chart(bars_graph, use_container_width=True)

with col4:
    # Country selection dropdown
    country = st.selectbox("Select a country:", options=dropdown_options)

    # Update country graph based on selection
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
        hover_data={"value": ":,", "variable": False, "date": False},
    )
    fig.update_xaxes(rangeslider_visible=True)
    fig["data"][0]["line"]["color"] = "#e74c3c"
    fig["data"][1]["line"]["color"] = "#8e44ad"
    fig["data"][2]["line"]["color"] = "#27ae60"

    # Display the line graph
    st.plotly_chart(fig, use_container_width=True)
