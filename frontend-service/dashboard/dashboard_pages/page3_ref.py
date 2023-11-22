# ./dashboard_pages/page3_ref.py

import dash
from dash import Dash, dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

from dashboard_init import app, style_dict, logger, session, session_feature_service
from app.feature_service_models import Minute_price_data
from app.prediction_metrics import get_live_predictions_df, get_live_predicted_results_df
from app.prediction_service_models import Prediction_records
from app.query import current_datetime, get_active_model_ids, get_model_ids, get_live_minute_price_dataframe, get_model_info, get_labels_details

import datetime
import pandas as pd
import time


print(get_active_model_ids(logger, session)[0])
# Define content for page 2
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H6("Select Deployed Model"),
                    html.Div(id='active-models-input', children=''),
                    dcc.Dropdown(
                        id='active-models-dropdown',
                        options=[
                            {'label': 'activate', 'value': 'True'}
                            ],
                        value=get_active_model_ids(logger, session)[0]
                    ),
                    #html.Div(id='output')
                    ##Input('selected-model', 'children'),
                    #html.Div(id='active-models-id-list'),
                    html.Div(id='selected-model-details')
                ], style=style_dict)], width=3),
        dbc.Col([
            dbc.Row([
                html.Div([
                    html.H6("Live Prediction"),
                    html.Div(id='selected-model'),
                    html.Div(id='prediction-details'),
                    dcc.Graph(id='prediction-graph', animate=True),
                    dcc.Interval(
                        id='graph-update',
                        interval=10*1000
                        ),
                    ], style=style_dict)]),
            dbc.Row([
                html.Div([
                    html.H6("Prediction History Table"),
                    html.Div(id='prediction-table')
                    ], style=style_dict)])
                ], width=9)
        ])
    ], fluid=True)

# active model options
@app.callback(
        Output('active-models-dropdown', 'options'),
        Input('active-models-input', 'children')
)
def active_models_dropdown_options(active_models_id_input):
    active_models = get_active_model_ids(logger, session)
    print(active_models)
    #print(active_models)
    #if not active_models_id_input:
    #    return "No active models currently available. Activate deployment on previous page."

    #active_models_list_items = [html.Li(html.A(f"{model['label']}", href="#", id=f"selected-model-{model['label']}")) for model in active_models]
    return active_models #html.Ol(active_models_list_items)

# display selected prediction model
@app.callback(
        Output('selected-model-details', 'children'),
        Output('selected-model', 'children'),
        Input('active-models-dropdown', 'value')
        #[Input(f"selected-model-{model['label']}", 'n_clicks') for model in get_active_model_ids(logger, session)]
    )
def display_selected_model(selected_model):
    if not selected_model:
        return "No details.", "No model selected."
    # # Find which link was clicked
    # ctx = dash.callback_context
    # if not ctx.triggered:
    #     return ""
    # else:
    #     link_id = ctx.triggered[0]['prop_id'].split('.')[0]
    #     selected_model = link_id.split('-')[-1]

    model_details = get_model_info(logger, session, selected_model)

    return [
        html.Hr(),
        html.H6(f"Model details:"),
        html.Li(f"model type: {model_details.model_type}"),
        html.Li(f"lookahead: {model_details.labels.lookahead_value} hours"),
        html.Li(f"percent change threshold: {model_details.labels.percent_change_threshold}%")
        ], selected_model

# prediction graph
@app.callback(
        Output('prediction-details', 'children'),
        [Input('selected-model', 'children'),
         Input('graph-update', 'n_intervals')]
)
def next_prediction_details(selected_model_input, n_intervals):
    # load live websocket price
    try:
        live_price_df = pd.read_csv('./dataframes/data_buffer_df.csv')
        live_price_value = live_price_df['websocket_price'].iloc[-1]
        live_datetime_value = live_price_df['websocket_datetime'].iloc[-1]
    except pd.errors.EmptyDataError as e:
        print(f"error occurred: {e}")
        raise PreventUpdate

    # get model lookahead value
    model_details = get_model_info(logger, session, selected_model_input)
    lookahead = int(model_details.labels.lookahead_value) - 3

    # get prediction record dataframe
    try:
        df_predictions = get_live_predictions_df(logger, session, selected_model_input)
        next_predicted_datetime = df_predictions['datetime'].iloc[lookahead]
        next_predicted_price_threshold = df_predictions['prediction_price_threshold'].iloc[lookahead]
        next_predicted_classification = df_predictions['predicted'].iloc[lookahead]
    except IndexError as e:
        print(f"error occurred: {e}")
        next_predicted_datetime = df_predictions['datetime'].iloc[0]
        next_predicted_price_threshold = df_predictions['prediction_price_threshold'].iloc[0]
        next_predicted_classification = df_predictions['predicted'].iloc[0]

    next_predicted_datetime_dt = next_predicted_datetime.to_pydatetime()
    live_datetime_value_dt = datetime.datetime.strptime(live_datetime_value, "%Y-%m-%d %H:%M:%S.%f")

    # calculate the time difference in seconds
    time_difference_seconds = (next_predicted_datetime_dt - live_datetime_value_dt).total_seconds()

    # # results logic
    # if time_difference_seconds < 0:
    #     next_price_prediction_minutes = 0
    #     next_price_prediction_seconds = 0
    #     next_price_prediction_message = None
        
    #     # current prediction message
    #     if next_predicted_classification == 0 and live_price_value < next_predicted_price_threshold:
    #         prediction_message = "Correct!"
    #     elif next_predicted_classification == 1 and live_price_value >= next_predicted_price_threshold:
    #         prediction_message = "Correct!"
    #     else:
    #         prediction_message = "Wrong!"
    # else:

    # Convert seconds to minutes
    next_price_prediction_minutes = int(time_difference_seconds // 60)
    next_price_prediction_seconds = int(time_difference_seconds % 60)
    next_price_prediction_message = f"{next_price_prediction_minutes} minutes, {next_price_prediction_seconds} seconds"
    prediction_message = ""

    # current prediction message
    if next_predicted_classification == 0:
        prediction_message = f"Prediction: less than {next_predicted_price_threshold}" # in {next_price_prediction_message}"
    elif next_predicted_classification == 1:
        prediction_message = f"Prediction: greater than {next_predicted_price_threshold}" # in {next_price_prediction_message}"

    return html.Div([
                html.Div([
                    html.H6(""),
                    html.H4(f"Current price: {live_price_value}"),
                          ]),
                html.Div([
                    html.H4(f"{prediction_message}")
                          ]),
                html.Div([
                    html.H4(f"{next_price_prediction_message}")
                ])
                ], style={'fontWeight': 'normal', 'display': 'flex', 'justify-content': 'space-between'})

# prediction graph
@app.callback(
        Output('prediction-graph', 'figure'),
        [Input('selected-model', 'children'),
         Input('graph-update', 'n_intervals')]
)
def prediction_graph(selected_model_input, n_intervals):
    # get prediction record dataframe
    try:
        df_minute_price = get_live_minute_price_dataframe(logger, session_feature_service)
    except IndexError as e:
        print(f"error occurred: {e}")

    # get prediction record dataframe
    try:
        df_predictions = get_live_predictions_df(logger, session, selected_model_input)
    except IndexError as e:
        print(f"error occurred: {e}")

    # load live websocket price
    try:
        live_price_df = pd.read_csv('./dataframes/data_buffer_df.csv')
        live_price_value = live_price_df['websocket_price'].iloc[-1]
        live_datetime_value = live_price_df['websocket_datetime'].iloc[-1]
    except pd.errors.EmptyDataError as e:
        print(f"error occurred: {e}")
        raise PreventUpdate

    # define subplot
    fig = go.Figure()
    
    # add prediction threshold values
    fig.add_trace(
        go.Scatter(
            x=df_predictions['datetime'],
            y=df_predictions['prediction_price_threshold'],
            line=dict(color='grey'),
            name='prediction',
            mode='lines+markers'
            )
        )
    
    # add minute price data and current price
    fig.add_trace(
        go.Scatter(
            x=df_minute_price['datetime'],
            y=df_minute_price['minute_price'],
            line=dict(color='blue'),
            name='price',
            yaxis='y',
            mode='lines'
            )
        )
    

    
    fig.update_traces(line=dict(width=1), selector=dict(mode='lines'))

    # Add a vertical dashed line and annotations
    fig.update_layout(
        shapes=[
            dict(
                type='line',
                x0=live_datetime_value,
                x1=live_datetime_value,
                y0=live_price_value * 0.9,
                y1=live_price_value * 1.1,
                line=dict(
                    color='rgba(0, 0, 0, 0.5)',
                    width=1,
                    dash='dash'
                    )
                )
            ],
        annotations=[
            # live price
            dict(
                x=live_datetime_value, y=live_price_value,
                xref="x", yref="y",
                text="X",
                showarrow=True,
                ax=0,
                ay=0,
                font=dict(color="black", size=14)
                ),
            dict(
                x=df_minute_price['datetime'][0] - pd.Timedelta(hours=4), y=df_minute_price['minute_price'].max() * 1.1,
                xref="x", yref="y",
                text="past",
                showarrow=False,
                font=dict(color="black", size=12)
                ),
            # 'future' indicator
            dict(
                x=df_minute_price['datetime'][0] + pd.Timedelta(hours=4), y=df_minute_price['minute_price'].max() * 1.1,
                xref="x", yref="y",
                text="future",
                showarrow=False,
                font=dict(color="black", size=12)
                )
            ]
        )
    
    #####
    # get current minute datetime and slice df_predictions
    current_minute_datetime = df_minute_price['datetime'].iloc[0].strftime('%Y-%m-%d %H:%M')
    df_predictions = df_predictions[df_predictions['datetime'] >= current_minute_datetime]
    
    datetime_lst = df_predictions['datetime'].to_list()
    prediction_price_threshold_lst = df_predictions['prediction_price_threshold'].to_list()
    predicted_lst = df_predictions['predicted'].to_list()
    
    # Initialize segments for the trace
    segments = []
    
    # Initialize the first segment
    segment = {
        "datetime": [datetime_lst[0]],
        "prediction_price_threshold": [prediction_price_threshold_lst[0]],
        "predicted": predicted_lst[0]
        }
    
    # Loop through the data and create segments based on changes in binary value
    for i in range(1, len(predicted_lst)):
        if predicted_lst[i] == segment["predicted"]:
            segment["datetime"].append(datetime_lst[i])
            segment["prediction_price_threshold"].append(prediction_price_threshold_lst[i])
        else:
            segment["datetime"].append(datetime_lst[i])
            segment["prediction_price_threshold"].append(prediction_price_threshold_lst[i])
            segments.append(segment)
            segment = {
                "datetime": [datetime_lst[i]],
                "prediction_price_threshold": [prediction_price_threshold_lst[i]],
                "predicted": predicted_lst[i]
                }
    
    # Append the last segment
    segments.append(segment)
    
    # Loop through each segment and add trace to the figure
    for segment in segments:
        if segment["predicted"] == 1:
            # Horizontal line at max y
            y_line = [df_minute_price['minute_price'].max() * 1.15] * len(segment["datetime"])
            fig.add_trace(go.Scatter(x=segment["datetime"], y=y_line, line=dict(color='rgba(255,255,255,0)', width=0), showlegend=False))
            # Fill area above price threshold
            fill_to = 'tonexty'
            color_to = 'green'
            fig.add_trace(go.Scatter(x=segment["datetime"], y=segment["prediction_price_threshold"], mode='lines', fill=fill_to, line=dict(color=color_to, width=0), opacity=0.2, showlegend=False))
        else:
            # Horizontal line at min y
            y_line = [df_minute_price['minute_price'].min() * 0.9] * len(segment["datetime"])
            fig.add_trace(go.Scatter(x=segment["datetime"], y=segment["prediction_price_threshold"], line=dict(color='rgba(255,255,255,0)', width=0), showlegend=False))
            # Fill area below price threshold
            fill_to = 'tonexty'
            color_to = 'red'
            fig.add_trace(go.Scatter(x=segment["datetime"], y=y_line, mode='lines', fill=fill_to, line=dict(color=color_to, width=0), opacity=0.2, showlegend=False))
            
    # add legend indicator for red and green
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', marker=dict(color='red'), name='prediction (0)', showlegend=True, visible='legendonly'))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', marker=dict(color='green'), name='prediction (1)', showlegend=True, visible='legendonly'))
    #####

    # update xaxis range options
    fig.update_layout(
        showlegend=True,
        xaxis=dict(
            range=[df_minute_price['datetime'].iloc[60*6], df_predictions['datetime'].max()],
            ),
        yaxis=dict(
            title="price (usd)"
            )
        )
    
    return fig

# prediction table
@app.callback(
        Output('prediction-table', 'children'),
        Input('selected-model', 'children')
)
def prediction_table(selected_model_input):
    df_predicted_results = get_live_predicted_results_df(logger, session, selected_model_input)

    return [
        dash_table.DataTable(
            id='table',
            columns=[{"name": col, "id": col} for col in df_predicted_results.columns],
            data=df_predicted_results.reset_index().to_dict('records'),
            style_table={'margin': 'auto'},
            style_header={
                'backgroundColor': 'lightgrey',
                'fontWeight': 'bold',
                'fontSize': '12px',
                'fontFamily': 'Arial'
                },
            style_cell={
                'fontSize': '12px',
                'fontFamily': 'Arial',
                'textAlign': 'center'
                }
            )
        ]