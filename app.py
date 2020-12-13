import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import datetime as dt
from datetime import date
import flask
import os
import pandas as pd
import time

from gs_quant.session import GsSession, Environment
from gs_quant.data import Dataset

import config

app = dash.Dash(__name__)

amc_df = pd.read_csv('./data/AMC.csv')
dis_df = pd.read_csv('./data/DIS.csv')
nflx_df = pd.read_csv('./data/NFLX.csv')
roku_df = pd.read_csv('./data/ROKU.csv')
six_df = pd.read_csv('./data/SIX.csv')
spot_df = pd.read_csv('./data/SPOT.csv')

dfs = {
    'AMC': amc_df,
    'DIS': dis_df,
    'NFLX': nflx_df,
    'ROKU': roku_df,
    'SIX': six_df,
    'SPOT': spot_df,
}

for df in dfs.values():
    initial_share_price = df['Close'].iloc[0]
    df['YTD Gain (%)'] = (df['Close'] - initial_share_price) / initial_share_price * 100

CLIENT_ID = config.CLIENT_ID
CLIENT_SECRET = config.CLIENT_SECRET
START, END = date(2020, 1, 2), date(2020, 12, 11) 
GsSession.use(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
who_dataset = Dataset('COVID19_COUNTRY_DAILY_WHO')
who_data_frame = who_dataset.get_data(countryId='US', start=START, end=END)


app.layout = html.Div([
    
    dcc.Dropdown(
        id='stock-ticker-input',
        options=[
            {
                'label': key,
                'value': str(key)
            }
            for key in dfs.keys()
        ],
        value=['NFLX',],
        multi=True
    ),

    dcc.Graph(id="graph"),
])

@app.callback(
    Output("graph", "figure"), 
    [Input("stock-ticker-input", "value")])
def display_(tickers):

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for ticker in tickers:
        # Add traces
        fig.add_trace(
            go.Scatter(x=dfs[ticker]['Date'], y=dfs[ticker]['YTD Gain (%)'], name="{} Closing Price".format(ticker)),
            secondary_y=False,
        )

    fig.add_trace(
        go.Scatter(x=who_data_frame.index, y=who_data_frame['totalConfirmed'], name="Covid Cases (Total)"),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
        title_text="Entertainment Stock Performance & Covid Cases"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Date")

    # Set y-axes titles
    fig.update_yaxes(
        title_text="YTD Gain (%)", 
        secondary_y=False)
    fig.update_yaxes(
        title_text="<b>Total Confirmed Covid Cases", 
        secondary_y=True)

    return fig

app.run_server(debug=True)