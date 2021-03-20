import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

import pandas as pd
import joblib
import plotly.express as px
import plotly.figure_factory as ff


import requests
import copy

layout = dict(
    #autosize=True,
    #automargin=True,
    #margin=dict(l=20, r=20, b=20, t=30),
    hovermode="closest",
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    font_color ="#2c3e50",
    xaxis_showgrid=False,
    yaxis_showgrid=False
)



