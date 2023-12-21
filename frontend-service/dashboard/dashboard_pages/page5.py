# ./dashboard_pages/page4.py

from dash import html

# define static layout for Grafana embedding
layout = html.Div([
    html.Iframe(
        src="http://34.72.106.126/d/df879a67-6383-4619-84b2-f123b9ebbf1f/price-prediction-app-dashboard?orgId=1&from=now-3h&to=now&refresh=auto&kiosk",
        width="100%",
        height="675",
        style={'border': 'none'}
    ),
    html.Footer(html.Small("powered by Grafana"),
                style={'color': 'white'})
], style={'backgroundColor': 'black',
          'height': '100vh'})