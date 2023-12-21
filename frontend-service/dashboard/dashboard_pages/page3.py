# ./dashboard_pages/page3.py

from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import datetime
import pandas as pd
import plotly.graph_objects as go

from app.query import current_datetime, get_model_info, get_active_models, get_live_minute_price_dataframe
from app.prediction_metrics import get_current_prediction, get_live_predictions_df, get_live_predicted_results_df
from dashboard_init import app, logger, session_prediction_service, session_feature_service, style_dict

# define initial scatter plot
initial_df_minute = get_live_minute_price_dataframe(
    logger, session_feature_service)
initial_fig = go.Figure()
initial_fig.add_trace(
    go.Scatter(
        x=initial_df_minute['datetime'],
        y=initial_df_minute['minute_price'],
        line=dict(color='blue'),
        name='price',
        yaxis='y',
        mode='lines'
    )
)
initial_fig.update_layout(yaxis=dict(title='price (usd)'))
initial_fig.update_traces(line=dict(width=1),
                          selector=dict(mode='lines'))

# page 3 layout
layout = dbc.Container([
    dcc.Location(id='url-page3', refresh=True),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Select Deployed Model"),
                dcc.Dropdown(
                    id='metrics-dropdown',
                    options=[
                        {'label': 'Running Accuracy',
                            'value': 'running_accuracy'},
                        {'label': 'Test Accuracy', 'value': 'test_accuracy'},
                        {'label': 'Train Accuracy', 'value': 'train_accuracy'},
                        {'label': 'True Positive Rate', 'value': 'running_TPR'},
                        {'label': 'False Positive Rate', 'value': 'running_FPR'}
                    ],
                    value='running_accuracy'
                ),
                html.Div(id='model-list'),
                dcc.Store(id='stored-model-id'),
                html.Div(id='model-details'),
                html.P(''),
                dcc.Link("model performance", href="/dashboard_pages/page4")
            ], style=style_dict, className="auto-width")
        ], width=3),

        dbc.Col([
            dbc.Row([
                html.Div([
                    html.H5("Live Prediction"),
                    html.Div(id='live-prediction'),
                    dcc.Interval(
                        id='prediction-dashboard-interval',
                        interval=1*1000
                    ),
                    dcc.Graph(id='prediction-graph',
                              figure=initial_fig, animate=True),
                    dcc.Interval(
                        id='prediction-graph-interval',
                        interval=5*1000
                    ),
                ], style=style_dict)
            ]),
        ], width=7),

        dbc.Col([
            dbc.Row([
                html.Div([
                    html.H5("Next Predictions"),
                    html.Div(id='future-prediction-table')
                ])
            ], style=style_dict)
        ], width=2)

    ])
], fluid=True)


# select metric and sort active models and return model selection table
@app.callback(
    Output('model-list', 'children'),
    Input('metrics-dropdown', 'value')
)
def metrics_dropdown(metric_value):
    if not metric_value:
        return "Sort models by metric."

    active_models = get_active_models(
        logger, session_prediction_service, metric_value)
    if not active_models:
        return "No active models. Activate models on previous page."
    
    # format metric call
    metric_value_str = metric_value.replace("_", " ")
    
    # ranked models HTML table
    metric_table = html.Table([
        html.Thead(
            html.Tr(
                [html.Th("Model ID"), html.Th(f"{metric_value_str}")])
        ),
        html.Tbody([
            html.Tr(
                [html.Td(html.A(model[0], href=f"#/selected-{model[0]}",
                                id=f"selected-{model[0]}")),
                 html.Td(model[1], style={'textAlign': 'center'})]) for model in active_models]
        )
    ])

    return metric_table


# model details after clicking model link
@app.callback(
    Output('model-details', 'children'),
    Output('stored-model-id', 'data'),
    Input('url-page3', 'href'),
    prevent_initial_call=True
)
def model_details(href_input):
    # check href address has model ID extension split address to get model ID
    if "-" not in list(href_input):
        model_id_clicked = None
        return "", model_id_clicked
    else:
        model_id_clicked = str(href_input.split('-')[1])

    # check model ID present in href query model info
    model_info_query = get_model_info(
        logger, session_prediction_service, model_id_clicked)
    if not model_info_query:
        return "No model details"

    model_details = html.Div([
        html.Hr(),
        html.H6("Details:"),
        html.Li(f"model type: {model_info_query.model_type}"),
        html.Li(f"labels ID: {model_info_query.model_labels_id}"),
        html.Li(
            f"lookahead: {model_info_query.labels.lookahead_value} hours"),
        html.Li(
            f"percent change: {model_info_query.labels.percent_change_threshold}%"),
        html.P(""),
        html.Footer(html.Small(f"ID: {model_id_clicked}")),
        html.Footer(html.Small(
            f"prediction type: {model_info_query.prediction_type}"))
    ])

    return model_details, model_id_clicked


# update live prediction info
@app.callback(
    Output('live-prediction', 'children'),
    Input('stored-model-id', 'data'),
    Input('prediction-dashboard-interval', 'n_intervals')
)
def update_live_prediction(stored_model_id, n_intervals):

    # load live websocket price and datetime values
    try:
        live_price_df = pd.read_csv('./dataframes/data_buffer_df.csv')
        live_price_value = live_price_df['websocket_price'].iloc[-1]
        live_datetime_value = live_price_df['websocket_datetime'].iloc[-1]
    except pd.errors.EmptyDataError as e:
        print(f"error occurred: {e}")
        raise PreventUpdate

    # format live_price_value
    live_price_value_formatted = "${:,.2f}".format(live_price_value)

    # format live_datetime time and date values
    live_datetime_value_obj = datetime.datetime.strptime(
        live_datetime_value, "%Y-%m-%d %H:%M:%S.%f")
    live_datetime_value_time = live_datetime_value_obj.strftime("%H:%M:%S")
    live_datetime_value_date = live_datetime_value_obj.strftime("%Y-%m-%d")

    # check no model ID selected, return only price
    if not stored_model_id:
        current_price_details = html.Div([
            html.P("current:"),
            html.H4(f"{live_price_value_formatted}"),
            html.H4(f"{live_datetime_value_date}, {live_datetime_value_time}"),
            html.P(""),
            html.Footer(html.Small("Select a model to view predictions."))
        ], style={'flex': 1,
                  'padding': '10px',
                  'backgroundColor': 'lightblue'})

        return current_price_details

    # get model info from stored_model_id
    model_info_query = get_model_info(
        logger, session_prediction_service, stored_model_id)

    # get next prediction datetime value for model selected
    next_prediction_datetime = current_datetime()[1] + datetime.timedelta(hours=1)

    # get next prediction info
    current_prediction_info = get_current_prediction(
        logger, session_prediction_service, stored_model_id, next_prediction_datetime)
    next_prediction_price = "${:,.2f}".format(
        current_prediction_info.prediction_threshold)
    next_prediction_classification = current_prediction_info.prediction_value

    # prediction 'greater' or 'less' than message
    if next_prediction_classification == 0:
        prediction_direction_message = "less than"
        prediction_classification = "negative"
        prediction_classification_sign = "-"

        # check against current price value for False or Positive status
        if float(current_prediction_info.prediction_threshold) >= live_price_value:
            prediction_status = "true"
            prediction_indicator = "green"

        else:
            prediction_status = "false"
            prediction_indicator = "red"

    elif next_prediction_classification == 1:
        prediction_direction_message = "greater than"
        prediction_classification = "positive"
        prediction_classification_sign = "+"

        # check against current price value for False or Positive status
        if float(current_prediction_info.prediction_threshold) <= live_price_value:
            prediction_status = "true"
            prediction_indicator = "green"
        else:
            prediction_status = "false"
            prediction_indicator = "red"

    # next prediction datetime
    next_prediction_datetime = current_prediction_info.lookahead_datetime

    # percent error message
    try:
        percent_error = ((float(current_prediction_info.prediction_threshold) -
                         live_price_value) / float(current_prediction_info.prediction_threshold)) * 100
        percent_error_formatted = round(percent_error, 2)
    except:
        raise PreventUpdate

    current_prediction_details = html.Div([
        html.Div([
            html.P("current:"),
            html.H4(f"{live_price_value_formatted}"),
            html.H6(
                f"{live_datetime_value_date}, {live_datetime_value_time}"),
            html.P(""),
            html.Footer(html.Small(f"ID: {stored_model_id}")),
            html.Footer(html.Small(
                f"prediction type: {model_info_query.prediction_type}"))
        ], style={'flex': 1, 'padding': '10px', 'backgroundColor': 'lightblue'}),
        html.Div([
            html.P("prediction:"),
            html.H4(
                f"{prediction_direction_message}: {next_prediction_price}"),
            html.H6(
                f"classification: {prediction_classification} ({prediction_classification_sign})"),
            html.H6(f"next prediction: {next_prediction_datetime}")
        ], style={'flex': 1, 'padding': '10px', 'backgroundColor': 'lightblue'}),
        html.Div([
            html.P("message:"),
            html.H4(f"percent error: {percent_error_formatted}%"),
            html.H6(
                f"status: {prediction_status} {prediction_classification}"),
            html.Img(
                src=f'../assets/{prediction_indicator}_circle_dot.png', alt='image')
        ], style={'flex': 1, 'padding': '10px', 'backgroundColor': 'lightblue'})
    ], style={'display': 'flex', 'flexDirection': 'row'})

    return current_prediction_details


# update prediction price graph
@app.callback(
    Output('prediction-graph', 'figure'),
    Input('stored-model-id', 'data'),
    Input('prediction-graph-interval', 'n_intervals')
)
def update_graph(stored_model_id, n_intervals):
    # initialize plotly Figure
    fig = go.Figure()

    # add minute price data
    df_minute = get_live_minute_price_dataframe(
        logger, session_feature_service)
    fig.add_trace(
        go.Scatter(
            x=df_minute['datetime'],
            y=df_minute['minute_price'],
            line=dict(color='blue'),
            name='price',
            yaxis='y',
            mode='lines'
        )
    )

    # load live websocket price and datetime values
    try:
        live_price_df = pd.read_csv('./dataframes/data_buffer_df.csv')
        live_price_value = live_price_df['websocket_price'].iloc[-1]
        live_datetime_value = live_price_df['websocket_datetime'].iloc[-1]
    except pd.errors.EmptyDataError as e:
        print(f"error occurred: {e}")
        raise PreventUpdate

    # vertical dashed line and annotations
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
            # 'past' indicator
            dict(
                x=df_minute['datetime'][0] - pd.Timedelta(hours=4),
                y=live_price_value * 1.1,
                xref="x", yref="y",
                text="past",
                showarrow=False,
                font=dict(color="black", size=12)
            ),
            # 'future' indicator
            dict(
                x=df_minute['datetime'][0] + pd.Timedelta(hours=4),
                y=live_price_value * 1.1,
                xref="x", yref="y",
                text="future",
                showarrow=False,
                font=dict(color="black", size=12)
            )
        ]
    )

    # add prediction price down/up data and arrows if model selected
    if stored_model_id:
        # get df_predictions info
        df_predictions = get_live_predictions_df(
            logger, session_prediction_service, stored_model_id)

        # define a custom arrow marker
        arrow_marker_up = dict(
                symbol="triangle-up",
                size=8,
                opacity=0.8,
                line=dict(width=2, color='darkgrey'),
                color='lightgreen'
                )
        
        # define a custom arrow marker
        arrow_marker_down = dict(
                symbol="triangle-down",
                size=8,
                opacity=0.8,
                line=dict(width=2, color='darkgrey'),
                color='red'
                )
        
        # add price down prediction data
        df_predictions_down = df_predictions[df_predictions['predicted'] == 0]
        fig.add_trace(
            go.Scatter(
                x=df_predictions_down['datetime'],
                y=df_predictions_down['prediction_price_threshold'],
                #line=dict(color='orange'),
                name='prediction down',
                yaxis='y',
                mode='markers',
                marker=arrow_marker_down
            )
        )

        # add price up prediction data
        df_predictions_up = df_predictions[df_predictions['predicted'] == 1]
        fig.add_trace(
            go.Scatter(
                x=df_predictions_up['datetime'],
                y=df_predictions_up['prediction_price_threshold'],
                name='prediction up',
                yaxis='y',
                mode='markers',
                marker=arrow_marker_up
            )
        )

        # update xaxis range options
        fig.update_layout(
            showlegend=True,
            xaxis=dict(
                range=[df_minute['datetime'].min(),
                       df_predictions['datetime'].max() + pd.Timedelta(hours=4)],
            ),
            yaxis=dict(
                title="price (usd)"
            )
        )

        fig.update_traces(line=dict(width=1), selector=dict(mode='lines'))

        return fig

    # update xaxis range options for df_minute only
    fig.update_layout(
        showlegend=True,
        xaxis=dict(
            range=[df_minute['datetime'].min(), df_minute['datetime'].max() +
                   pd.Timedelta(hours=4)],
        ),
        yaxis=dict(
            title="price (usd)"
        )
    )

    fig.update_traces(line=dict(width=1), selector=dict(mode='lines'))

    return fig


# populate and return future preditions table for stored model ID
@app.callback(
    Output('future-prediction-table', 'children'),
    Input('stored-model-id', 'data')
)
def future_predictions_table(stored_model_id):
    # check stored model present
    if not stored_model_id:
        return "Select a model to view live prediction."

    # get model info from stored_model_id
    model_info_query = get_model_info(
        logger, session_prediction_service, stored_model_id)

    # get future prediction results
    df_future_predictions = get_live_predictions_df(
        logger, session_prediction_service, stored_model_id, current_datetime()[1])

    # check prediction results exist yet
    if len(df_future_predictions) == 0:
        return "no predictions yet."

    return [
        html.Footer(html.Small(f"ID: {stored_model_id}")),
        html.Footer(html.Small(
            f"prediction type: {model_info_query.prediction_type}")),
        html.P(""),
        dash_table.DataTable(
            id='table',
            columns=[{"name": col, "id": col}
                     for col in df_future_predictions.columns],
            data=df_future_predictions.reset_index().to_dict('records'),
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