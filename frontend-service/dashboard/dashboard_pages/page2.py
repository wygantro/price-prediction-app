# ./dashboard_pages/page2.py

# import dash

from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.figure_factory as ff
import plotly.graph_objects as go

import numpy as np
import pandas as pd

from app.query import get_labels_ids, get_labels_details, get_model_ids, get_model_info, get_mlflow_model_info
from app.train_test import datetime_train_test_ranges

from dashboard_init import app, df, logger, session_mlflow, session_prediction_service, style_dict

# define initial scatter plot
initial_fig = go.Figure()
initial_fig.add_trace(
    go.Scatter(
        x=df['hour_datetime_id'],
        y=df['btc_hour_price_close'],
        mode='lines',
        name='BTC/USD (hour)'
    )
)
initial_fig.update_layout(yaxis=dict(title='price (usd)'))
initial_fig.update_traces(line=dict(width=1),
                          selector=dict(mode='lines'))


# page 2 layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Available Labels"),
                dcc.Dropdown(id='labels-id-dropdown', value=None),
                html.Div(id='labels-id-details')
            ], style=style_dict),
            html.Div([
                html.H5("Trained Models"),
                dcc.Dropdown(id='models-id-dropdown'),
                html.Div(id='models-id-details'),
                dcc.Checklist(
                    id='deploy-model-checkbox',
                    options=[{'label': 'activate', 'value': 'True'}],
                    value=[],
                    inline=True
                ),
                html.Div(id='model-deployment-message'),
            ], style=style_dict),
            html.Footer(html.Small(dcc.Link("powered by MLflow",
                                            href="http://34.31.62.132:5000/#/models",
                                            target="_blank")))], width=3),
        dbc.Col([
            dbc.Row([
                html.Div([
                    html.H5("Price Profile"),
                    dcc.Graph(id='price-profile-graph',
                              figure=initial_fig, animate=True),
                    html.Div(id='price-profile-details')
                ], style=style_dict)
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H5("Confusion Matrix"),
                        html.Div(id='confusion-matrix'),
                    ], style=style_dict)
                ], width=6),
                dbc.Col([
                    html.Div([
                        html.H5("ROC Curve"),
                        html.Div(id='roc-curve'),
                    ], style=style_dict)
                ], width=6)
            ])
        ], width=9)
    ])
], fluid=True)


# labels options
@app.callback(
    Output('labels-id-dropdown', 'options'),
    Input('labels-id-dropdown', 'value')
)
def labels_dropdown_options(labels_id_input):
    available_labels_dropdown = get_labels_ids(
        logger, session_prediction_service)
    if not available_labels_dropdown:
        available_labels_dropdown = [{"label": "None", "value": None}]
        return available_labels_dropdown
    return available_labels_dropdown


# labels details
@app.callback(
    Output('labels-id-details', 'children'),
    Input('labels-id-dropdown', 'value')
)
def labels_dropdown_details(labels_id_input):
    if not labels_id_input:
        return "Select Labels ID to see its details and trained models."

    # query labels ID details
    labels_details = get_labels_details(
        logger, session_prediction_service, labels_id_input)
    if not labels_details:
        return f"No details found for ID {labels_id_input}"

    labels_id_details = [
        html.P(""),
        html.H6("Details:"),
        html.Hr(),
        html.Li(f"output: {labels_details.target_output}"),
        html.Li(f"start: {labels_details.labels_start_datetime}"),
        html.Li(f"end: {labels_details.labels_end_datetime}"),
        html.Li(f"lookahead: {labels_details.lookahead_value} hours"),
        html.Li(
            f"percent change: + {labels_details.percent_change_threshold} %"),
        html.Li(f"trained models: {len(labels_details.model_info)}")
    ]

    return labels_id_details


# select available models from labels ID input
@app.callback(
    Output('models-id-dropdown', 'options'),
    Input('labels-id-dropdown', 'value')
)
def models_dropdown_options(labels_id_input):
    if not labels_id_input:
        available_models_dropdown = [{"label": "None", "value": None}]
        return available_models_dropdown

    # query available models from labels ID input
    available_models_dropdown = get_model_ids(
        logger, session_prediction_service, labels_id_input)
    if not available_models_dropdown:
        available_models_dropdown = [{"label": "None", "value": None}]
        return available_models_dropdown

    return available_models_dropdown


# trained model details
@app.callback(
    Output('models-id-details', 'children'),
    Output('deploy-model-checkbox', 'value'),
    Input('models-id-dropdown', 'value'),
    prevent_initial_call=True
)
def models_dropdown_details(models_id_input):
    if not models_id_input:
        checkmark_value = []
        return "No models available for labels selected", checkmark_value

    # get prediction-service and mlflow model details from model ID input
    mlflow_model_details = get_mlflow_model_info(
        logger, session_mlflow, models_id_input)
    model_details = get_model_info(
        logger, session_prediction_service, models_id_input)
    if not mlflow_model_details or not model_details:
        checkmark_value = []
        return f"No details found for ID {models_id_input}", checkmark_value

    # get database deployment status and update checkmark value
    deployed_status = model_details.deployed_status
    if deployed_status:
        checkmark_value = ['True']
    elif not deployed_status:
        checkmark_value = []

    # define model metrics
    model_metrics_query = get_model_info(
        logger, session_prediction_service, models_id_input)
    train_accuracy_str = "{:.1%}".format(model_metrics_query.train_accuracy)
    test_accuracy_str = "{:.1%}".format(model_metrics_query.test_accuracy)

    model_id_details = [
        html.P(""),
        html.H6("Details:"),
        html.Hr(),
        html.Li(f"prediction type: {mlflow_model_details[0]}"),
        html.Li(f"model type: {mlflow_model_details[1]}"),
        html.Li(f"split type: {mlflow_model_details[2]}"),
        html.Li(f"train accuracy: {train_accuracy_str}"),
        html.Li(f"test accuracy: {test_accuracy_str}")
    ]

    return model_id_details, checkmark_value


# model deployment status
@app.callback(
    Output('model-deployment-message', 'children'),
    Input('models-id-dropdown', 'value'),
    Input('deploy-model-checkbox', 'value')
)
def update_deployed_status(models_id_input, deploy_model_checkbox):
    # get model info
    model_details = get_model_info(
        logger, session_prediction_service, models_id_input)
    if not model_details:
        return ""

    # get deployment status from prediction-service-db
    deployment_status = model_details.deployed_status
    if deploy_model_checkbox != deployment_status:
        if deploy_model_checkbox:
            model_details.deployed_status = True
            session_prediction_service.commit()
            session_prediction_service.close()

            # MLflow model to 'Production' database update
            update_statement = """
                                UPDATE model_versions
                                SET current_stage = :new_value
                                WHERE name = :record_id_name AND version = :record_id_version
                            """
            params = {
                'new_value': 'Production',
                'record_id_name': models_id_input,
                'record_id_version': 1
            }

            session_mlflow.execute(update_statement, params)
            session_mlflow.commit()
            session_mlflow.close()

            return [
                html.Div('Deployed!'),
                dbc.NavLink("view here", href=f"/dashboard_pages/page3",
                            style={"color": "blue", "text-decoration": "underline"})
            ]

        elif not deploy_model_checkbox:
            model_details.deployed_status = False
            session_prediction_service.commit()
            session_prediction_service.close()

            ### MLflow model to 'Staging' database update ###
            update_statement = """
                                UPDATE model_versions
                                SET current_stage = :new_value
                                WHERE name = :record_id_name AND version = :record_id_version
                            """
            params = {
                'new_value': 'Staging',
                'record_id_name': models_id_input,
                'record_id_version': 1
            }

            session_mlflow.execute(update_statement, params)
            session_mlflow.commit()
            session_mlflow.close()
            ######

            return [
                html.P('Deployment stopped.'),
            ]


# price profile graph
@app.callback(
    Output('price-profile-graph', 'figure'),
    Input('labels-id-dropdown', 'value'),
    # Input('models-id-dropdown', 'value'),
    prevent_initial_call=True
)
def price_profile_graph(labels_id_input):  # , model_id_input):
    df = pd.read_csv('./dataframes/hour_data.csv')

    if not labels_id_input:
        # redefine and return initial default scatter plot
        fig = go.Figure()

        # remove all shapes from previous callbacks
        fig['layout']['shapes'] = []

        fig.add_trace(
            go.Scatter(
                x=df['hour_datetime_id'],
                y=df['btc_hour_price_close'],
                mode='lines',
                name='BTC/USD (hour)'
            )
        )
        # update y-axis and trace
        fig.update_layout(yaxis=dict(title='price (usd)'))
        fig.update_traces(line=dict(width=1),
                          selector=dict(mode='lines'))

        return fig

    # graph labeled price region
    if labels_id_input:
        # get labels info from database
        labels_details = get_labels_details(
            logger, session_prediction_service, labels_id_input)
        start_date = labels_details.labels_start_datetime
        end_date = labels_details.labels_end_datetime

        # convert datetime ID column to pandas datetime objects
        df['hour_datetime_id'] = pd.to_datetime(df['hour_datetime_id'])

        # define range for dataframe based on labels info
        start_date_i = df[df['hour_datetime_id'] == start_date].index.item()
        end_date_i = df[df['hour_datetime_id'] == end_date].index.item()
        df_labeled = df.iloc[start_date_i:end_date_i]
        labels_datetime_list = df_labeled['hour_datetime_id'].to_list()

        # reintialized figure with labels region and adjust opacity for non labeled
        fig = go.Figure()
        fig['layout']['shapes'] = []

        fig.add_trace(
            go.Scatter(
                x=df['hour_datetime_id'],
                y=df['btc_hour_price_close'],
                mode='lines',
                name='BTC/USD',
                opacity=0.5
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df_labeled['hour_datetime_id'],
                y=df_labeled['btc_hour_price_close'],
                mode='lines',
                name='labeled price'
            )
        )

        # update figure shading train/test regions for model ID input
        model_id_input = False  # currently muted
        if model_id_input:
            # define list of tuples to shade train and test regions on graph
            datetime_train_test_ranges_list = datetime_train_test_ranges(
                labels_datetime_list, train_ratio=0.8)

            # update figure
            fig.update_layout(
                shapes=[
                    dict(
                        type="rect",
                        xref="x",
                        yref="paper",
                        x0=start,
                        y0=0,
                        x1=end,
                        y1=1,
                        fillcolor=fillcolor,
                        opacity=0.5,
                        layer="below",
                        line_width=0
                    ) for start, end, fillcolor in datetime_train_test_ranges_list[0]
                ],
                # add annotations to both sides of the vertical line
                annotations=[
                    dict(
                        x=datetime_train_test_ranges_list[1],
                        y=max(df['btc_hour_price_close'])*0.9,
                        xref="x", yref="y",
                        text="Train",
                        showarrow=False,
                        font=dict(color="black", size=12)
                    ),
                    dict(
                        x=datetime_train_test_ranges_list[2],
                        y=max(df['btc_hour_price_close'])*0.9,
                        xref="x", yref="y",
                        text="Test",
                        showarrow=False,
                        font=dict(color="black", size=12)
                    )
                ]
            )

            # update price trace range
            fig.update_layout(
                showlegend=True,
                xaxis=dict(
                    range=[min(labels_datetime_list),
                           max(labels_datetime_list)],
                    rangeselector=dict(
                        buttons=list([
                            dict(count=len(
                                labels_datetime_list), label='train/test region', step='hour', stepmode='backward'),
                            dict(step='all')
                        ])
                    ),
                    type='date'
                ),
                yaxis=dict(
                    title='price (usd)'
                )
            )

            # update y-axis and trace
            fig.update_layout(yaxis=dict(title='price (usd)'))
            fig.update_traces(line=dict(width=1),
                              selector=dict(mode='lines'))

            return fig

        else:
            # update y-axis and trace
            fig.update_layout(yaxis=dict(title='price (usd)'))
            fig.update_traces(line=dict(width=1),
                              selector=dict(mode='lines'))

            return fig


# price profile details
@app.callback(
    Output('price-profile-details', 'children'),
    Input('labels-id-dropdown', 'value'),
    Input('models-id-dropdown', 'value')
)
def price_profile_details(labels_id_input, model_id_input):
    if not labels_id_input and not model_id_input:
        return "No labels or models selected"

    # check for model ID input
    if labels_id_input and not model_id_input:
        # return selected labels ID
        price_profile_details = html.Div([
            html.Div([html.H6(f'Label ID: {labels_id_input}')]),
            html.Div([html.H6(f'Model ID: select a trained model!'),]),
            html.Div([html.H6('')])
        ], style={'display': 'flex',
                  'justify-content': 'space-between'})

        return price_profile_details

    # return selected labels and model ID
    price_profile_details = html.Div([
        html.Div([html.H6(f'Label ID: {labels_id_input}')]),
        html.Div([html.H6(f'Model ID: {model_id_input}')]),
        html.Div([html.H6('')])
    ], style={'fontWeight': 'normal',
              'display': 'flex',
              'justify-content': 'space-between'})

    return price_profile_details


# confusion matrix graph
@app.callback(
    Output('confusion-matrix', 'children'),
    Input('models-id-dropdown', 'value')
)
def update_confusion_matrix_graph(model_id_input):
    # check for model ID input
    if not model_id_input:
        return "No models selected"

    # get model details
    model_details = get_model_info(
        logger, session_prediction_service, model_id_input)
    if not model_details:
        return f"No data available for model {model_id_input}"

    # load confusion matrix binary and convert to array
    confusion_matrix = np.frombuffer(
        model_details.model_binaries.confusion_matrix_binary,
        dtype=np.uint64).reshape(2, 2)
    labels = [0, 1]

    # graph confusion matrix
    fig = ff.create_annotated_heatmap(
        confusion_matrix,
        x=labels,
        y=labels,
        colorscale='Blues',
        showscale=True
    )

    # define dcc Graph child with fig
    confusion_matrix_fig_child = dcc.Graph(figure=fig, animate=True)

    return confusion_matrix_fig_child


# roc curve graph
@app.callback(
    Output('roc-curve', 'children'),
    Input('models-id-dropdown', 'value')
)
def update_roc_curve_graph(model_id_input):
    # check for model ID input
    if not model_id_input:
        return "No models selected"

    # get model details
    model_details = get_model_info(
        logger, session_prediction_service, model_id_input)
    if not model_details:
        return f"No data available for model {model_id_input}"

    # load roc curve details
    roc_auc = model_details.roc_auc
    fpr = np.frombuffer(model_details.model_binaries.fpr_binary)
    tpr = np.frombuffer(model_details.model_binaries.tpr_binary)
    thresholds = np.frombuffer(model_details.model_binaries.thresholds_binary)

    # define graph layout
    layout = go.Layout(
        xaxis=dict(title='False Positive Rate'),
        yaxis=dict(title='True Positive Rate'),
        hovermode='closest'
    )

    # define roc curve values
    fig = go.Figure(
        data=[go.Scatter(
            x=fpr,
            y=tpr,
            mode='lines',
            hoverinfo="text+x+y",
            text=[f"Threshold: {str(t)}" for t in thresholds],
            name='ROC Curve'
        )
        ], layout=layout)

    # define dcc Graph child with fig
    roc_curve_fig_child = [
        html.P(f'Area = {roc_auc:.2f}'),
        dcc.Graph(figure=fig, animate=True)
    ]

    return roc_curve_fig_child
