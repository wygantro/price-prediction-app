# dashboard.py

from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import datetime
import pandas as pd

from dashboard_init import app, logger, session_prediction_service
from dashboard_pages import page1, page2, page3, page4, page5
from app.query import current_datetime, get_active_models
from app.prediction_metrics import get_avg_prediction

# # set custom favicon .ico file
# favicon_path = "assets/yellow_circle_dot.ico"

# app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    # html.Link(
    #     rel='icon',
    #     href=favicon_path,
    # ),
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("1) Configure Dataframe",
                        href="/dashboard_pages/page1")),
            dbc.NavItem(dbc.NavLink("2) Models",
                        href="/dashboard_pages/page2")),
            dbc.NavItem(dbc.NavLink("3) Live Predictions",
                        href="/dashboard_pages/page3")),
            dbc.NavItem(dbc.NavLink("System Info",
                        href="/dashboard_pages/page5"))
        ],
        brand=html.H4("Price Prediction App"),
        color="#050505",
        dark="#02f543"
    ),
    html.Div(id='page-content')
])

# home page content
home_layout = html.Div([
    # left side
    html.Div([
        html.Div([
            html.H5(
                "An end-to-end solution for real time financial price predictions"),
            html.Ul([
                html.Li("Access over 50 macro economic features updated hourly"),
                html.Li("Label historic price movements and download CSV dataframe"),
                html.Li("Compare trained machine learning models"),
                html.Li("Deploy and get live predictions")])
        ], style={'flex': 1, 'textAlign': 'left', 'padding': '40px'})
    ], style={'width': '50%', 'float': 'left'}),
    # right side
    html.Div(id='model-serving-table',
             style={'width': '50%', 'float': 'left'}),
    dcc.Interval(
        id='table-update',
        interval=1.5*1000
    ),
    html.Div(style={'width': '80vw', 'display': 'inline-block'}),
    html.Div(style={'display': 'flex'}, children=[
        # first column
        html.Div([
            html.Img(src='./assets/configure-dataframe-v2.png',
                         alt='image', style={'width': '20%', 'height': 'auto'}),
            html.H3("Step 1"),
            html.Div(style={'width': '10vw', 'display': 'inline-block'}),
            html.H5("Configure Dataframe"),
            html.P(
                "Specify range, explore features, and label historic price movement for training."),
        ], style={'flex': 1,
                  'textAlign': 'center',
                  'padding': '40px',
                  'backgroundColor': '#e4eaf5',
                  'borderRadius': '5px',
                  'margin-left': '80px',
                  'margin-right': '80px'}),
        # second column
        html.Div([
            html.Img(src='./assets/explore-models-v2.png',
                         alt='image', style={'width': '20%', 'height': 'auto'}),
            html.H3("Step 2"),
            html.Div(style={'width': '10vw', 'display': 'inline-block'}),
            html.H5("Explore Trained Models"),
            html.P(
                "Compare models on similiar training data and deploy for real time predictions."),
        ], style={'flex': 1,
                  'textAlign': 'center',
                  'padding': '40px',
                  'backgroundColor': '#e4eaf5',
                  'borderRadius': '5px',
                  'margin-left': '80px',
                  'margin-right': '80px'}),
        # third column
        html.Div([
            html.Img(src='./assets/visualize-predictions-v2.png',
                         alt='image', style={'width': '20%', 'height': 'auto'}),
            html.H3("Step 3"),
            html.Div(style={'width': '10vw', 'display': 'inline-block'}),
            html.H5("Live Price Predictions"),
            html.P(
                "Visualize live price predictions and performance!"),
        ], style={'flex': 1,
                  'textAlign': 'center',
                  'padding': '40px',
                  'backgroundColor': '#e4eaf5',
                  'borderRadius': '5px',
                  'margin-left': '80px',
                  'margin-right': '80px'})
    ]),
    html.Br(),
    html.Div([
        html.A(html.Img(src='./assets/LI-In-Bug.png', alt='image',
                        style={'width': '45px',
                               'height': '40px'}),
               href='https://www.linkedin.com/in/robert-wygant/', target='_blank'),
        html.P("   "),
        html.A(html.Img(src='./assets/github-mark.png', alt='image',
                        style={'margin-left': '10px',
                               'width': '40px',
                               'height': '40px'}),
               href='https://github.com/wygantro/price-prediction-app', target='_blank'),
        html.P("   "),
        html.A(html.H4("Docs"), href="/assets/documentation.html",
               target="_blank",
               style={'margin-left': '10px', 'margin-top': '10px'})
    ], style={'flex': 1,
              'textAlign': 'left',
              'padding': '40px',
              'display': 'flex',
              'position': 'absolute',
              'bottom': 0})
])


@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/dashboard_pages/page1':
        return page1.layout
    elif pathname == '/dashboard_pages/page2':
        return page2.layout
    elif pathname == '/dashboard_pages/page3':
        return page3.layout
    elif pathname == '/dashboard_pages/page4':
        return page4.layout
    elif pathname == '/dashboard_pages/page5':
        return page5.layout
    else:
        return home_layout


@app.callback(
    Output('model-serving-table', 'children'),
    Input('table-update', 'n_intervals')
)
def update_table(n_intervals):
    # get number of active models
    active_models = get_active_models(logger, session_prediction_service)
    if not active_models:
        num_active_models = 0
    num_active_models = len(active_models)

    # load live BTC/USD websocket price and datetime values
    try:
        live_price_df = pd.read_csv('./dataframes/data_buffer_df.csv')
        live_price_value = live_price_df['websocket_price'].iloc[-1]
        live_datetime_value = live_price_df['websocket_datetime'].iloc[-1]
    except pd.errors.EmptyDataError as e:
        raise PreventUpdate
    
    # format live_price_value
    live_price_value_formatted = "${:,.2f}".format(live_price_value)

    # load live ETH/USD websocket price and datetime values
    try:
        live_price_eth_df = pd.read_csv('./dataframes/eth_data_buffer_df.csv')
        live_price_eth_value = live_price_eth_df['websocket_price'].iloc[-1]
        #live_datetime_eth_value = live_price_df['websocket_datetime'].iloc[-1]
    except pd.errors.EmptyDataError as e:
        raise PreventUpdate
    
    # format live_price_value
    live_price_eth_value_formatted = "${:,.2f}".format(live_price_eth_value)

    # get average prediction value
    avg_predictions = get_avg_prediction(
        logger, session_prediction_service, current_datetime()[1])

    # define 'greater than' or 'less than' message
    if avg_predictions[0] > 0.5:
        prediction_msg = "greater than: "
    else:
        prediction_msg = "less than : "

    # format average prediction price threshold
    avg_predictions_formatted = "${:,.2f}".format(avg_predictions[1])

    # format live_datetime time and date values
    live_datetime_value_obj = datetime.datetime.strptime(
        live_datetime_value, "%Y-%m-%d %H:%M:%S.%f")
    live_datetime_value_time = live_datetime_value_obj.strftime("%H:%M:%S")
    live_datetime_value_date = live_datetime_value_obj.strftime("%Y-%m-%d")

    table_content = html.Div([
        html.Table([
            # header
            html.Tr([
                html.Th('asset pair',
                        style={'text-align': 'center',
                               'padding-left': '20px',
                               'padding-right': '20px'}),
                html.Th('serving',
                        style={'text-align': 'center',
                               'padding-left': '20px',
                               'padding-right': '20px'}),
                html.Th('current price',
                        style={'text-align': 'center',
                               'padding-left': '20px',
                               'padding-right': '20px'}),
                html.Th('average prediction',
                        style={'text-align': 'center',
                               'padding-left': '20px',
                               'padding-right': '20px'}),
                html.Th('')
            ], style={'text-align': 'center'}),
            # BTC/USD
            html.Tr([
                html.Td([
                    html.Img(src='./assets/bitcoin.png',
                             style={'width': '20%',
                                    'height': 'auto',
                                    'object-fit': 'cover'}),
                    'BTC/USD'], style={'width': '120px', 'padding': '10px'}),
                html.Td(f'{num_active_models} models',
                        style={'padding': '10px'}),
                html.Td(f'{live_price_value_formatted}',
                        style={'padding': '10px'}),
                html.Td(f'{prediction_msg} {avg_predictions_formatted}', style={
                        'padding': '10px'}),
                html.Td(dcc.Link("view", href='/dashboard_pages/page3'),
                        style={'padding': '10px'})
            ], style={'text-align': 'left'}),
            # ETH/USD
            html.Tr([
                html.Td([
                    html.Img(src='./assets/Ethereum-ETH-Logo.png',
                             style={'width': '20%',
                                    'height': 'auto',
                                    'object-fit': 'cover'}),
                    'ETH/USD'], style={'width': '120px', 'padding': '10px'}),
                html.Td('N/A', #f'{num_active_models} models',
                        style={'padding': '10px'}),
                html.Td(f'{live_price_eth_value_formatted}',
                        style={'padding': '10px'}),
                html.Td('N/A', #f'{prediction_msg} {avg_predictions_formatted}',
                        style={'padding': '10px'}),
                html.Td(dcc.Link("view", href='/dashboard_pages/page3'),
                        style={'padding': '10px'})
            ], style={'text-align': 'left'})
        ]),
        html.Footer(html.Small(
            f"last updated: {live_datetime_value_date}, {live_datetime_value_time}"))
    ], style={'flex': 1,
              'textAlign': 'left',
              'padding': '40px',
              'border-collapse': 'collapse'}, className='table-bordered')

    return table_content


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
