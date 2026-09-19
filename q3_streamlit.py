"""
Question 3: Schiphol Departures Dashboard (2 points in total)

Run this file from a terminal with:
    streamlit run q3_streamlit.py

For this question, you will create a dashboard showing a few 
departure flights from Schiphol airport. The dashboard needs to satisfy
the following requirements:
(1) have two multiselect widgets to select airlines and destination countries (1 point)
(2) display the flight data as a dataframe (1 point)
"""

# install all required packages first
import pydeck as pdk
import streamlit as st
import pandas as pd


# set the streamlit app main page configuration
st.set_page_config(page_title="Schiphol Departures", layout="wide")
st.title("Schiphol Departures Dashboard")
st.caption("10 sample flights departing Amsterdam Schiphol Airport (AMS).")

# ---------------------------------------------------------------------------
# Get Flight Data
# ---------------------------------------------------------------------------

# Schiphol's coordinates -- every flight in this exercise departs from here.
# We use UPPER_CASE style naming for constants
SCHIPHOL_LAT = 52.31
SCHIPHOL_LON = 4.76

# One dictionary per flight. You can add your own row the same way if you want!
FLIGHTS = [
    {"flight_number": "VY8301", "airline": "Vueling",        "destination_city": "Barcelona",    "destination_country": "Spain",          "departure_time": "10:20", "arrival_lat": 41.30, "arrival_lon": 2.08},
    {"flight_number": "U28673", "airline": "easyJet",        "destination_city": "London",       "destination_country": "United Kingdom", "departure_time": "10:20", "arrival_lat": 51.15, "arrival_lon": -0.19},
    {"flight_number": "KL9857", "airline": "KLM",            "destination_city": "Brussels",     "destination_country": "Belgium",        "departure_time": "10:20", "arrival_lat": 50.90, "arrival_lon": 4.48},
    {"flight_number": "KL1615", "airline": "KLM",            "destination_city": "Milan",        "destination_country": "Italy",          "departure_time": "10:25", "arrival_lat": 45.45, "arrival_lon": 9.28},
    {"flight_number": "SK552",  "airline": "SAS",            "destination_city": "Copenhagen",   "destination_country": "Denmark",        "departure_time": "10:25", "arrival_lat": 55.62, "arrival_lon": 12.66},
    {"flight_number": "KL615",  "airline": "KLM",            "destination_city": "Portland",     "destination_country": "United States",  "departure_time": "10:25", "arrival_lat": 45.59, "arrival_lon": -122.60},
    {"flight_number": "DL73",   "airline": "Delta",          "destination_city": "Atlanta",      "destination_country": "United States",  "departure_time": "10:25", "arrival_lat": 33.64, "arrival_lon": -84.43},
    {"flight_number": "FR421",  "airline": "Ryanair",        "destination_city": "Dublin",       "destination_country": "Ireland",        "departure_time": "10:30", "arrival_lat": 53.42, "arrival_lon": -6.27},
    {"flight_number": "LO266",  "airline": "LOT",            "destination_city": "Warsaw",       "destination_country": "Poland",         "departure_time": "10:30", "arrival_lat": 52.17, "arrival_lon": 20.97},
    {"flight_number": "KL591",  "airline": "KLM",            "destination_city": "Johannesburg", "destination_country": "South Africa",   "departure_time": "10:35", "arrival_lat": -26.14, "arrival_lon": 28.25},
]


def get_flights():
    """Return the 10 sample flights as a pandas DataFrame."""
    df = pd.DataFrame(FLIGHTS)
    # add departure airport Schiphol's latitude and longitude
    df["dep_lat"] = SCHIPHOL_LAT
    df["dep_lon"] = SCHIPHOL_LON
    return df

df = get_flights()

# ---------------------------------------------------------------------------
# Dashboard Sidebar filters
# ---------------------------------------------------------------------------

st.sidebar.header("Filters")

# TODO: complete the code to sort airlines (df['airline']) by alphabetic order
airlines = 
# add a multiselect widget for choosing airlines to display
chosen_airlines = st.sidebar.multiselect("Airline", airlines, default=airlines)

# TODO: complete the code to sort countries (df["destination_country"]) by alphabetic order
countries = 
# TODO: complete the code to add a multiselect widget for choosing destination countries
chosen_countries = 

filtered = df[df["airline"].isin(chosen_airlines) & df["destination_country"].isin(chosen_countries)]

# ---------------------------------------------------------------------------
# Table
# ---------------------------------------------------------------------------

st.subheader("Flights")

# TODO: complete the code to display the dataframe of filtered flights
# see documentation: https://docs.streamlit.io/develop/api-reference/data/st.dataframe
st.dataframe()

# ---------------------------------------------------------------------------
# Map: one arc per flight, from Schiphol to its destination
# ---------------------------------------------------------------------------

st.subheader("Flight Map")

arc_layer = pdk.Layer(
    "ArcLayer",
    data=filtered,
    get_source_position=["dep_lon", "dep_lat"],
    get_target_position=["arrival_lon", "arrival_lat"],
    get_source_color=[255, 140, 0],   # orange at Schiphol
    get_target_color=[0, 128, 255],   # blue at the destination
    get_width=3,
    pickable=True,
)

# this sets the default initial view point
view_state = pdk.ViewState(latitude=20, longitude=20, zoom=1, pitch=30) 

st.pydeck_chart(pdk.Deck(
    layers=[arc_layer],
    initial_view_state=view_state,
    tooltip={"text": "{flight_number} to {destination_city}"},
))

st.caption("orange = departure (from Schiphol), blue = arrival.")
