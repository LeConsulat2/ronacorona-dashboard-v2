import streamlit as st
import pandas as pd
import plotly.express as px

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


# Embed custom CSS to force dark theme
# st.markdown(
#     """
#     <style>
#     /* Adjust the vh for the main container */
#     .main .block-container {
#         height: 90vh; /* Adjust this value as needed */
#         max-height: 90vh;
#         width: 100vw; /* Adjust this value as needed */
#         max-width: 100vw; /* Adjust this value as needed */
#         overflow-y: auto; /* Add scrolling if needed */
#     }

#     /* Remove the header background */
#     .stApp > header {
#         background-color: #111111;
#     }

#     /* Additional styles for the Streamlit app */
#     .stApp {
#         margin: auto;
#         font-family: -apple-system, BlinkMacSystemFont, sans-serif;
#         overflow: auto;
#         background: #111111;
#         color: white; /* Set text color to white */
#         animation: gradient 15s ease infinite;
#         background-size: 400% 400%;
#         background-attachment: fixed;
#     }

#     /* Make sure the text inside other containers is also white */
#     .main .block-container, .main .block-container div, .main .block-container p, .main .block-container h1, .main .block-container h2, .main .block-container h3, .main .block-container .stMarkdown, .main .block-container .stDataFrame {
#         color: white;
#     }

#     /* Set background for dataframe elements */
#     .stDataFrame, .stDataFrame table {
#         background-color: #222222;
#         color: white;
#     }

#     /* Style the dropdown */
#     .stSelectbox {
#         color: white;
#         background-color: #333333;
#     }

#     /* Style the plotly graphs */
#     .stPlotlyChart {
#         background-color: #111111;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )
