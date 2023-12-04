# ./dashboard_pages/page1.py

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

import datetime
import pandas as pd

from app.prediction_service_models import Labels_directory
from app.binary_classification import binary_classification_lookahead, datetime_classified_ranges
from app.query import create_df_labels

from dashboard_init import app, df, logger, session_prediction_service, style_dict

# define intial range values
min_value = 0
max_value = len(df) - 1
step_value = len(df) // 24

# define initial scatter plot with selected target output
initial_fig = go.Figure()
initial_fig.add_trace(
    go.Scatter(
        x=df['hour_datetime_id'],
        y=df['btc_hour_price_close'],
        mode='lines',
        name='BTC/USD (hour)'
    )
)

# update y-axis and trace
initial_fig.update_layout(yaxis=dict(title='price (usd)'))
initial_fig.update_traces(line=dict(width=1),
                          selector=dict(mode='lines'))

# page 1 layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col(html.Div([
                    html.H5("Select Range"),
                    dcc.Dropdown(
                        id='dropdown-select-output',
                        options=[
                            {'label': 'BTC/USD (hour)',
                             'value': 'btc_hour_price_close'}
                        ],
                        value='btc_hour_price_close',
                        multi=False
                    ),
                    html.Div(id='selected-output'),
                    html.Div('select range'),
                    dcc.RangeSlider(
                        id='date-range-slider',
                        min=min_value,
                        max=max_value,
                        step=step_value,
                        value=[min_value, max_value],
                        marks={i: '' for i in range(
                            min_value, max_value, int(step_value))}
                    ),
                    dcc.Checklist(
                        id='graph-range-checkbox',
                        options=[
                            {'label': 'apply range', 'value': 'True'}
                        ],
                        value=[],
                        inline=True
                    )
                ], style=style_dict), width=6),

                dbc.Col(html.Div([
                    html.H5("Available Features"),
                    dcc.Dropdown(
                        id='dropdown-available-inputs',
                        options=[{'label': col, 'value': col}
                                 for col in df.columns[2:]],
                        value='federal_funds_daily',
                        multi=False
                    ),
                    html.Div(id='selected-feature'),
                    dcc.Checklist(
                        id='graph-feature-checkbox',
                        options=[
                            {'label': 'add to graph', 'value': 'True'}
                        ],
                        value=[],
                        inline=True
                    )
                ], style=style_dict), width=6)
            ]),

            dbc.Row([
                dbc.Col(html.Div([
                    html.H5("Graph"),
                    dcc.Graph(id='graph',
                              figure=initial_fig,
                              animate=True),
                    html.H6("Last updated: "),
                    html.Div(id='last-updated'),
                ], style=style_dict))
            ])
        ], width=9),

        dbc.Col(
            html.Div([
                html.Div([
                    html.H5("Label Output"),
                    html.H6("Lookahead timestep (hours): "),
                    dcc.Input(
                        id='lookahead-timestep',
                        type='number',
                        value=12,
                        step=1
                    ),
                    html.H6("Percent change threshold (%): "),
                    dcc.Slider(
                        id='lookahead-threshold',
                        min=0,
                        max=10,
                        value=2,
                        marks={i: str(i) for i in range(0, 11)},
                        step=0.5
                    ),
                    html.Br(),
                    html.H6("Label Summary:"),
                    html.Div(id='selected-labels-info'),
                    dcc.Checklist(
                        id='add-labels-checkbox',
                        options=[{'label': 'add to graph',
                                  'value': 'True'}],
                        value=[],
                        inline=True
                    ),
                    html.P(''),
                    html.H6("Save Labels"),
                    html.Button('Save', id='save-button', n_clicks=0),
                    html.Div(id='save-button-message')
                ], style=style_dict),
                dcc.Store(id='labels-id')
            ]), width=3)
    ])
], fluid=True)


# select target output
@app.callback(
    Output('selected-output', 'children'),
    Input('dropdown-select-output', 'value')
)
def select_target_output(selected_output):
    return f"selected output: {selected_output}"


# available features
@app.callback(
    Output('selected-feature', 'children'),
    Input('dropdown-available-inputs', 'value')
)
def select_feature(selected_feature):
    return f"selected feature: {selected_feature}"


# update graph with range, feature and label inputs
@app.callback(
    Output('graph', 'figure'),
    Output('last-updated', 'children'),
    Input('graph-range-checkbox', 'value'),
    Input('date-range-slider', 'value'),
    Input('graph-feature-checkbox', 'value'),
    Input('dropdown-available-inputs', 'value'),
    Input('lookahead-timestep', 'value'),
    Input('lookahead-threshold', 'value'),
    Input('add-labels-checkbox', 'value')
)
def update_graph(range_checkbox, range_value, graph_feature_checkbox,
                 graph_feature_value, lookahead_timestep,
                 lookahead_threshold, add_labels_checkbox):
    
    # load dataframe
    df = pd.read_csv('./dataframes/hour_data.csv')
    last_updated = df['hour_datetime_id'].iloc[-1]

    # set dataframe datetime range
    if range_checkbox and not graph_feature_checkbox:
        df = df.iloc[range_value[0]:range_value[1]]
        current_feature = []
    elif range_checkbox and graph_feature_checkbox:
        df = df.iloc[range_value[0]:range_value[1]]
        current_feature = graph_feature_value
    elif not range_checkbox and graph_feature_checkbox:
        current_feature = graph_feature_value
    else:
        current_feature = []

    # define initial scatter plot with selected target output
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df['hour_datetime_id'],
            y=df['btc_hour_price_close'],
            mode='lines',
            name='BTC/USD (hour)'
        )
    )

    # add selected feature trace if checkbox is checked
    if graph_feature_checkbox and current_feature == graph_feature_value:
        current_feature = graph_feature_value
        fig.add_trace(
            go.Scatter(
                x=df['hour_datetime_id'],
                y=df[graph_feature_value],
                mode='lines',
                name=graph_feature_value,
                yaxis='y2'
            )
        )

        # update secondary y axis specific to selected feature
        fig.update_layout(
            yaxis2=dict(
                title=graph_feature_value,
                overlaying='y',
                side='right',
                range=[min(df[graph_feature_value]),
                       max(df[graph_feature_value])]
            )
        )

    # update initial layout and trace
    fig.update_layout(
        yaxis_title="price (usd)",
        showlegend=True,
        xaxis=dict(
            range=[min(df['hour_datetime_id']),
                   max(df['hour_datetime_id'])]
        ),
        yaxis=dict(
            range=[min(df['btc_hour_price_close']),
                   max(df['btc_hour_price_close'])]
        )
    )

    fig.update_traces(line=dict(width=1),
                      selector=dict(mode='lines'))

    # add labels if checkbox is checked
    if add_labels_checkbox:
        hour_price_list = df['btc_hour_price_close'].to_list()
        labels_datetime_list = df['hour_datetime_id'].to_list()

        # define labeling range
        labels_list = binary_classification_lookahead(
            hour_price_list,
            lookahead=lookahead_timestep,
            threshold_percent=lookahead_threshold)[1]
        datetime_classified_ranges_list = datetime_classified_ranges(
            labels_list,
            labels_datetime_list)
        
        # add shading
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
                    fillcolor="lightgreen",
                    opacity=0.5,
                    layer="below",
                    line_width=0
                ) for start, end in datetime_classified_ranges_list
            ]
        )

    return fig, last_updated


# update label summary info
@app.callback(
    Output('selected-labels-info', 'children'),
    Input('dropdown-select-output', 'value'),
    Input('date-range-slider', 'value'),
    Input('lookahead-timestep', 'value'),
    Input('lookahead-threshold', 'value')
)
def update_label_info(selected_output, range_value,
                      lookahead_timestep, lookahead_threshold):
    df = pd.read_csv('./dataframes/hour_data.csv')

    # datetime range values from dataframe
    range_end = df['hour_datetime_id'].iloc[range_value[-1]]
    range_start = df['hour_datetime_id'].iloc[range_value[0]]

    # define HTML children output
    selected_labels_info = html.Div([
        html.Li(f"output: {selected_output}"),
        html.Li(f"start: {range_start}"),
        html.Li(f"end: {range_end}"),
        html.Li(f"lookahead: {lookahead_timestep} hours"),
        html.Li(f"percent change: + {lookahead_threshold} %"),
        html.P("")
    ])

    return selected_labels_info


# save label info to database
@app.callback(
    Output('save-button-message', 'children'),
    Output('labels-id', 'data'),
    Input('dropdown-select-output', 'value'),
    Input('date-range-slider', 'value'),
    Input('lookahead-timestep', 'value'),
    Input('lookahead-threshold', 'value'),
    Input('save-button', 'n_clicks')
)
def save_label_info(selected_output, range_value,
                    lookahead_timestep, lookahead_threshold, n_clicks):
    # default HTML output
    if not n_clicks:
        # load dataframe
        df = pd.read_csv('./dataframes/hour_data.csv')

        # resize dataframe
        df = df.iloc[range_value[0]:range_value[-1]]

        # define default HTML children output download CSV message
        rows, columns = df.shape
        labels_saved_info = html.Div([
                html.Hr(),
                html.P(""),
                html.H6("Dataframe Summary:"),
                html.P(f"rows: {rows}"),
                html.P(f"feature columns: {columns}"),
                html.Button("Download CSV", id="btn_csv"),
                dcc.Download(id="download-dataframe-csv"),
                html.P(""),
                html.Small("save labels first to download CSV"),
                dbc.NavLink("next page", href="/dashboard_pages/page2",
                            style={"color": "blue",
                                   "text-decoration": "underline"})
                ])
        
        labels_id = None
        
        return labels_saved_info, labels_id
    
    # check if saved button and update HTML and commit labels info to database
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'] == 'save-button.n_clicks':

        if n_clicks:
            # load dataframe
            df = pd.read_csv('./dataframes/hour_data.csv')

            # define labels info to commit
            labels_start_datetime_str = df['hour_datetime_id'].iloc[range_value[0]+1]
            labels_start_datetime = datetime.datetime.strptime(
                labels_start_datetime_str, "%Y-%m-%d %H:%M:%S")
            labels_end_datetime_str = df['hour_datetime_id'].iloc[range_value[-1]-1]
            labels_end_datetime = datetime.datetime.strptime(
                labels_end_datetime_str, "%Y-%m-%d %H:%M:%S")
            labels_created_datetime = datetime.datetime.now()
            labels_output = selected_output
            lookahead_value = lookahead_timestep
            percent_change_threshold = lookahead_threshold
            labels_id = f"labels_{int(labels_created_datetime.timestamp())}"

            # create labeled list
            df = df.iloc[range_value[0]:range_value[-1]]

            # create new database entry
            new_labels = Labels_directory(
                labels_id=labels_id,
                datetime_created=labels_created_datetime,
                target_output=labels_output,
                lookahead_value=lookahead_value,
                percent_change_threshold=percent_change_threshold,
                labels_start_datetime=labels_start_datetime,
                labels_end_datetime=labels_end_datetime
                )

            # commit labels info to database
            try:
                session_prediction_service.add(new_labels)
                session_prediction_service.commit()
            except:
                session_prediction_service.rollback()

            # define HTML children output saved labels message
            rows, columns = df.shape
            labels_saved_info = html.Div([
                html.P(""),
                html.H6("Saved!"),
                html.P(f"id: {labels_id}"),
                html.Hr(),
                html.P(''),
                html.H6("Dataframe Summary:"),
                html.P(f"rows: {rows}"),
                html.P(f"feature columns: {columns}"),
                html.Button("Download CSV", id="btn_csv"),
                dcc.Download(id="download-dataframe-csv"),
                html.P(''),
                dbc.NavLink("next page", href="/dashboard_pages/page2",
                            style={"color": "blue",
                                   "text-decoration": "underline"})
            ])

    else:
        labels_saved_info = None
        labels_id = None
    
    return labels_saved_info, labels_id


# download dataframe
@app.callback(
    Output('download-dataframe-csv', 'data'),
    Input("btn_csv", "n_clicks"),
    Input('labels-id', 'data'),
    prevent_initial_call=True
)
def download_dataframe(n_clicks, labels_id):
    if not n_clicks:
        return dash.no_update

    # reload hour_data and merge labels into dataframe
    df_hour_data = pd.read_csv('./dataframes/hour_data.csv')
    labels = create_df_labels(
        logger, session_prediction_service, df_hour_data, labels_id)
    dataframe = pd.merge(df_hour_data, labels,
                         on='hour_datetime_id', how='inner')

    return dcc.send_data_frame(dataframe.to_csv, "dataframe.csv")