# dashboard_init.py

import dash
import dash_bootstrap_components as dbc
import plotly.io as pio
from app.app_init import init_logger, create_db_models
from app.connect_db import connect_url
import pandas as pd
import logging

# initialize logs
logger = init_logger('frontend-service')

# initialize prediction-serivice-db session
database_service = 'prediction-service'
db_url = connect_url(database_service)
session_prediction_service = create_db_models(logger, db_url, database_service)
logger.log(logging.INFO, f"{database_service} session created")

database_service = 'feature-service'
db_url = connect_url(database_service)
session_feature_service = create_db_models(logger, db_url, 'feature-service')
logger.log(logging.INFO, f"{database_service} session created")

# define global style dictionary
style_dict = {
    'backgroundColor': '#f4f4f4',
    'margin': '5px',
    'padding': '15px',
    'border': '1px solid black',
    'borderRadius': '5px'
    }

pio.templates.default = "simple_white"
# "plotly"
# "plotly_white"
# "plotly_dark"
# "ggplot2"
# "seaborn"
# "simple_white"
# "none"

# load initial dataframe
file_path = './dataframes/hour_data.csv'
df = pd.read_csv(file_path)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = 'Price Prediction App'
server = app.server