# ./dashboard_pages/mlflow.py

from dash import html

# define static layout for Grafana embedding
layout = html.Div([
    html.Iframe(
        src="http://35.222.36.0:5000/#/models",
        width="100%",
        height="100%",
        style={'border': 'none'}
    ),
    html.Footer(html.Small("powered by Grafana mlflow test"),
                style={'color': 'white'})
], style={'backgroundColor': 'black',
          'height': '100vh'})