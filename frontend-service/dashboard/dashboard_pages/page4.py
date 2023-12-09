# ./dashboard_pages/page4.py

from dash import html

# define static layout for Grafana embedding
layout = html.Div([
    html.Iframe(
        src="http://34.72.106.126/d/b2f59277-b85e-40b9-ab89-52af577b980f/price-prediction-app-system-info?orgId=1&from=now-3h&to=now&refresh=auto&kiosk",
        width="100%",
        height="675",
        style={'border': 'none'}
    ),
    html.Footer(html.Small("powered by Grafana"),
                style={'color': 'white'})
], style={'backgroundColor': 'black',
          'height': '100vh'})