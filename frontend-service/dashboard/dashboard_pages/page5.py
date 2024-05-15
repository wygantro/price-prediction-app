# ./dashboard_pages/page5.py

from dash import html

# define static layout for Grafana embedding
layout = html.Div([
    html.Iframe(
        src="http://34.171.107.33/d/ddl0q224g6bk0c/price-prediction-app-dashboard?orgId=1&from=now-3h&to=now&refresh=auto&kiosk",
        width="100%",
        height="675",
        style={'border': 'none'}
    ),
    html.Footer(html.Small("powered by Grafana"),
                style={'color': 'white'})
], style={'backgroundColor': 'black',
          'height': '100vh'})
