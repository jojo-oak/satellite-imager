import ipywidgets as widgets
from pystac_client import Client
from IPython.display import display, clear_output
import pandas as pd
from shapely.geometry import shape
from datetime import date, datetime
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import os

token = ""

def display_collection(stac_url: str, name):
    # Try to connect
    try:
        catalog = Client.open(stac_url)
        print(f"✅ Connected to STAC at {stac_url}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    # Get collections
    collections = list(catalog.get_collections())
    num_collections = len(collections)
    print(f"📦 Number of collections found in {name} STAC: {num_collections}")

    if not collections:
        print("⚠️ No collections found.")
        return

    # Dropdown options
    options = {col.id: col for col in collections}
    dropdown = widgets.Dropdown(
        options=list(options.keys()),
        description='Collection:',
        layout=widgets.Layout(width='400px'),
        style={'description_width': 'initial'}
    )

    output = widgets.Output()

    # Function to display temporal extent
    def show_temporal_extent(collection_id):
        with output:
            clear_output()
            try:
                collection = options[collection_id]
                extent = collection.extent.temporal.to_dict().get('interval', [[None, None]])[0]
                start, end = extent

                start_str = datetime.fromisoformat(start.replace("Z", "+00:00")).strftime('%Y-%m-%d %H:%M:%S') if start else "❓ Not provided"
                end_str = datetime.fromisoformat(end.replace("Z", "+00:00")).strftime('%Y-%m-%d %H:%M:%S') if end else "❓ Not provided"

                print(f"📅 Temporal extent:\n→ {start_str} to {end_str}")
            except Exception as e:
                print(f"⚠️ Error fetching temporal extent: {e}")

    # Attach handler
    def on_change(change):
        if change["name"] == "value":
            show_temporal_extent(change["new"])

    dropdown.observe(on_change)

    # Display widgets
    display(dropdown, output)

    # Show initial value
    show_temporal_extent(dropdown.value)
    
    return dropdown

def plot_mapbox(
    geo_df: gpd.GeoDataFrame,
    color_column: str = None,
    center: dict = {"lat": 50, "lon": 10},
    zoom: float = 4,
    opacity: float = 0.3,
    map_style: str = "carto-positron"
):
    """
    Plots a choropleth map using Plotly and a GeoDataFrame.

    Parameters:
        geo_df (GeoDataFrame): The input GeoDataFrame with polygon geometries.
        color_column (str): Column name to color polygons by (optional).
        center (dict): Dict with 'lat' and 'lon' for map center.
        zoom (float): Zoom level for the map.
        opacity (float): Opacity for the polygons.
        map_style (str): Mapbox base style (e.g., 'carto-positron', 'open-street-map').
    """
    if geo_df.empty:
        print("⚠️ GeoDataFrame is empty. Cannot plot.")
        return

    fig = px.choropleth_mapbox(
        geo_df,
        geojson=geo_df.geometry,
        locations=geo_df.index,
        color=color_column if color_column else None,
    )

    fig.update_layout(
        mapbox=dict(
            style=map_style,
            center=center,
            zoom=zoom,
        ),
        margin={"r":0, "t":0, "l":0, "b":0},
    )

    fig.update_traces(marker_opacity=opacity)
    fig.show()

import ipywidgets as widgets
from IPython.display import display, clear_output
import plotly.express as px
import pandas as pd

def show_geo_map(geo_df, zoom=5, center_lat=50, center_lon=15):
    """
    Displays an interactive dropdown to explore items in a GeoDataFrame on a Mapbox choropleth.
    
    Parameters:
        geo_df (GeoDataFrame): GeoDataFrame with a 'start_datetime' column and geometry.
        zoom (int): Initial zoom level.
        center_lat (float): Latitude for initial map center.
        center_lon (float): Longitude for initial map center.
    
    Returns:
        dropdown (widgets.Dropdown): The dropdown widget (you can access .value for selected index).
    """
    # Ensure datetime format
    geo_df = geo_df.copy()
    geo_df['start_datetime'] = pd.to_datetime(geo_df['start_datetime'])

    # Create labeled options
    dropdown_options = [
        (f"{dt.strftime('%Y-%m-%d %H:%M:%S')} — item {i}", i)
        for i, dt in enumerate(geo_df['start_datetime'])
    ]

    dropdown = widgets.Dropdown(
        options=dropdown_options,
        description='Item:',
        layout=widgets.Layout(width='70%')
    )

    output = widgets.Output()

    def on_dropdown_change(change):
        if change['type'] == 'change' and change['name'] == 'value':
            with output:
                clear_output(wait=True)
                idx = change['new']
                item_choose = geo_df.iloc[[idx]]

                fig = px.choropleth_mapbox(
                    item_choose,
                    geojson=item_choose.geometry,
                    locations=item_choose.index,
                    center=dict(lat=center_lat, lon=center_lon),
                    mapbox_style='open-street-map',
                    zoom=zoom,
                    height=600,
                    width=1000
                )
                fig.update_traces(marker_opacity=0.5)
                fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
                fig.show()

    dropdown.observe(on_dropdown_change)
    display(dropdown, output)

    # Trigger initial display
    if dropdown_options:
        dropdown.value = dropdown_options[0][1]

    return dropdown
    
import jwt
import os
import requests
import time
import tempfile

def get_collgs_token():
    einfra_token = read_einfra_token()
    return einfra_token

def read_einfra_token():
    global token
    if not token:
        token = getpass.getpass()
    return token
