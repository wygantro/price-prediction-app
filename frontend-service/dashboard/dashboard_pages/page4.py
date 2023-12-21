# ./dashboard_pages/page4.py

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

# page 4 layout
layout = dbc.Container([
    dcc.Location(id='url-page4', refresh=True),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Select Ranking Metric"),
                dcc.Dropdown(
                    id='metrics-ranking-dropdown',
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
                html.Div(id='model-ranking-list'),
                dcc.Store(id='stored-ranking-model-id'),
                html.Div(id='model-ranking-details'),
                html.P(''),
                dcc.Link("live predictions", href="/dashboard_pages/page3")
            ], style=style_dict, className="auto-width")
        ], width=3),

        dbc.Col([
            dbc.Row([
                html.Div([
                    html.H5("Running Accuracy Error"),
                    html.Div(id='metric-graph-details'),
                    dcc.Graph(id='metric-comparison-graph'),
                ], style=style_dict)
            ]),
            dbc.Row([
                html.Div([
                    html.H5("Model Metric History"),
                    html.Div(id='model-history-table')
                ], style=style_dict)])
        ], width=8),
    ])
], fluid=True)


# select metric/sort models and return model selection table
@app.callback(
    Output('model-ranking-list', 'children'),
    Input('metrics-ranking-dropdown', 'value')
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


# model details and metric ranking options after clicking model link
@app.callback(
    Output('model-ranking-details', 'children'),
    Output('stored-ranking-model-id', 'data'),
    Input('url-page4', 'href')
)
def model_details(href_input):
    # check href address has model ID extension split address to get model ID
    if "-" not in list(href_input):
        model_id_clicked = get_active_models(logger, session_prediction_service, 'running_accuracy')[0][0]
    else:
        model_id_clicked = str(href_input.split('-')[1])

    # check model ID present in href query model info
    model_info_query = get_model_info(logger, session_prediction_service, model_id_clicked)
    if not model_info_query:
        stored_model_id = get_active_models(logger, session_prediction_service, 'running_accuracy')[0][0]
        model_info_query = get_model_info(logger, session_prediction_service, stored_model_id)

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


# update metric graph info
@app.callback(
    Output('metric-graph-details', 'children'),
    Input('stored-ranking-model-id', 'data'),
    prevent_initial_call=True
)
def update_live_prediction(stored_model_id):    
    # check model ID present in href query model info
    model_info_query = get_model_info(
        logger, session_prediction_service, stored_model_id)
    if not model_info_query:
        stored_model_id = get_active_models(logger, session_prediction_service, 'running_accuracy')[0][0]
        model_info_query = get_model_info(logger, session_prediction_service, stored_model_id)
    
    model_details = [
        html.P(""),
        html.Footer(html.Small(f"ID: {stored_model_id}")),
        html.Footer(html.Small(f"prediction type: {model_info_query.prediction_type}"))
        ]
    
    return model_details

# update metric comparison graph
@app.callback(
    Output('metric-comparison-graph', 'figure'),
    Input('stored-ranking-model-id', 'data')
)
def update_graph(stored_model_id):
    # initialize plotly Figure
    fig = go.Figure()

    # check and get stored model ID info
    model_info_query = get_model_info(logger, session_prediction_service, stored_model_id)
    if not model_info_query:
        stored_model_id = get_active_models(logger, session_prediction_service, 'running_accuracy')[0][0]
        model_info_query = get_model_info(logger, session_prediction_service, stored_model_id)

    # get prediction results
    df_prediction_results = get_live_predicted_results_df(
        logger, session_prediction_service, stored_model_id)
    
    # get test accuracy reference and calculate difference
    test_accuracy_ref = model_info_query.test_accuracy
    accuracy_diff_lst = [float(item) - test_accuracy_ref for item in df_prediction_results['running_accuracy']]

    # add metrics data to graph
    fig.add_trace(
        go.Scatter(
            x=df_prediction_results['datetime'],
            y=accuracy_diff_lst,
            line=dict(color='blue', width=1),
            name='accuracy (actual - test)',
            yaxis='y',
            mode='lines'
        )
    )

    # add a horizontal 0 difference reference line
    fig.add_shape(
        type="line",
        x0=df_prediction_results['datetime'].min(),
        x1=df_prediction_results['datetime'].max(),
        y0=0,
        y1=0,
        line=dict(color="red", width=2, dash='dash'),
        name='no difference reference'
    )
    fig.update_yaxes(range=[1, -1])
    fig.update_layout(showlegend=True)

    return fig


# populate and return model history table for stored model ID
@app.callback(
    Output('model-history-table', 'children'),
    Input('stored-ranking-model-id', 'data')
)
def prediction_table(stored_model_id):
    # check stored model present
    if not stored_model_id:
        return "Select a model to view prediction history."

    # get model info from stored_model_id
    model_info_query = get_model_info(
        logger, session_prediction_service, stored_model_id)

    # get prediction results
    df_prediction_results = get_live_predicted_results_df(
        logger, session_prediction_service, stored_model_id)

    # check prediction results exist yet
    if len(df_prediction_results) == 0:
        return "no prediction results available."

    model_history_table = [
        html.Footer(html.Small(f"ID: {stored_model_id}")),
        html.Footer(html.Small(
            f"prediction type: {model_info_query.prediction_type}")),
        html.P(""),
        dash_table.DataTable(
            id='table',
            columns=[{"name": col.replace("_", " "), "id": col}
                     for col in df_prediction_results.columns],
            data=df_prediction_results.reset_index().to_dict('records'),
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

    return model_history_table