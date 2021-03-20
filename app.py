import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash import no_update

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

import os
import sys
import copy
import time

from src.navbar import get_navbar
#from src.graphs import layout, graph_choropleth
import paho.mqtt.client as mqtt

# Creating the app

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    external_stylesheets = [dbc.themes.SUPERHERO,'/assets/styles.css']
) 

server=app.server


# STUFF

layout = dict(
    autosize=True,
    # automargin=True,
    margin=dict(l=20, r=20, b=20, t=30),
    hovermode="closest",
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    font_color ="#000",
    xaxis_showgrid=False,
    yaxis_showgrid=False
)


# -------------------------------------------------------------------------------
# MQTT Configurations
# -------------------------------------------------------------------------------

light_img_url = "light-unknown.png"
irrigation_img_url = "light-unknown.png"

def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  MQTT_TOPIC = [("topic/natikay",0), ("topic/natikay-irr",0)]
  client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):

    global light_img_url
    global irrigation_img_url

    if(msg.payload.decode() == "l0"):
        light_img_url = "light-off.png"
    
    elif(msg.payload.decode() == "l1"):
        light_img_url = "light-on.png"
    
    if(msg.payload.decode() == "i0"):
        irrigation_img_url = "irrigation_off.png"
    
    elif(msg.payload.decode() == "i1"):
        irrigation_img_url = "irrigation_on.gif"

    print(msg.payload.decode(), "   ", light_img_url)
    # client.disconnect()
    
client = mqtt.Client()
client.connect("mqtt.eclipseprojects.io", 1883, 60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_start()

# -------------------------------------------------------------------------------
# APP CONTENT
# -------------------------------------------------------------------------------

# -------------------------------------------------------------------------------
# 1st Row - Information Cards
# -------------------------------------------------------------------------------


card_temperature = dbc.Card(
    [
        dbc.Card(
            [
                html.Img(src="/assets/thermometer.svg", className="img-infocard")
            ], className="card-thermometer"
        ),

        html.P("25.38", className="text-temperature"),
        html.P("Celsius (°C)", className="text-infocard-unit"),

        
    ], className="card-infocard"
)

card_humidity = dbc.Card(
    [
        dbc.Card(
            [
                html.Img(src="/assets/humidity.svg", className="img-infocard")
            ], className="card-humidity"
        ),

        html.P("68.38", className="text-humidity"),
        html.P("Percent (%)", className="text-infocard-unit"),

        
    ], className="card-infocard"
)

card_air = dbc.Card(
    [
        dbc.Card(
            [
                html.Img(src="/assets/air-quality.svg", className="img-infocard")
            ], className="card-air"
        ),

        html.P("Good", className="text-air"),
        html.P("Air Quality", className="text-infocard-unit"),

        
    ], className="card-infocard"
)

card_plant = dbc.Card(
    [
        dbc.Card(
            [
                html.Img(src="/assets/plant-pot.svg", className="img-infocard")
            ], className="card-plant"
        ),

        html.P("4", className="text-plant"),
        html.P("Number of Plants", className="text-infocard-unit"),

        
    ], className="card-infocard"
)


# -------------------------------------------------------------------------------
# 2nd Row - Line Charts
# -------------------------------------------------------------------------------

card_soil_moisture = dbc.Card(
    [
        dbc.CardHeader("Soil Moisture History", className="card-header-light"),
        dbc.CardBody(
            [
                dcc.Graph(id="graph-soil-moisture-history", style={"height": "280px"})
            ]
        ),
    ], 
)

card_infocard_figure = dbc.Card(
    [
        dbc.CardHeader(
            [
                dbc.Select(
                    id="select-info",
                    options=[
                        {"label": "Temperature", "value": "temperature"},
                        {"label": "Humidity", "value": "humidity"}
                    ],
                    value="temperature",
                    style={"width": "240px", "float": "right"}
                )
            ], id="infocard-style", style={"background-color": "#b4af67"}
        ),

        dbc.CardBody(
            [
                dcc.Graph(id="graph-infocard-history", style={"height": "280px"})
            ]
        ),

    ]
)

# -------------------------------------------------------------------------------
# 3rd Row - Lighting and Irrigation
# -------------------------------------------------------------------------------

card_light = dbc.Card(
    [
        dbc.CardHeader("Lighting Control ", className="card-header-light"),
        dbc.CardBody(
            [
                html.Div(id="img-light"),
                #html.Img(id="img-light", className="img-light"),
                html.Div(
                    [
                        dbc.Button(id="btn-light-on", children="ON", color="success", className="mr-1 light-buttons-individual"),
                        dbc.Button(id="btn-light-off", children="OFF", color="danger", className="mr-1 light-buttons-individual"),
                        html.Div(id='hidden-div', style={'display':'none'}),
                        html.Div(id='hidden-div2', style={'display':'none'})
                    ], className="light-buttons"
                )

            ]
        ),
    ],
)


card_irrigation = dbc.Card(
    [
        dbc.CardHeader("Irrigation Control ", className="card-header-light"),
        dbc.CardBody(
            [
                html.Div(id="img-irrigation"),

                html.Div(
                    [
                        dbc.Button(id="btn-irrigation-on", children="ON", color="success", className="mr-1 light-buttons-individual"),
                        dbc.Button(id="btn-irrigation-off", children="OFF", color="danger", className="mr-1 light-buttons-individual"),
                        html.Div(id='hidden-div3', style={'display':'none'}),
                        html.Div(id='hidden-div4', style={'display':'none'})
                    ], className="light-buttons"
                )
            ]
        ),
    ], 
)


jumbotron = dbc.Jumbotron(
    [
        # html.H1("Jumbotron", className="display-3"),
        # html.P(
        #     "Use a jumbotron to call attention to "
        #     "featured content or information.",
        #     className="lead",
        # ),
        # html.Hr(className="my-2"),
        html.H4("Telco Customer Churn Analysis and Prediction"),
        # html.P(dbc.Button("Learn more", color="primary"), className="lead"),
    ], className="cover"
)


# -------------------------------------------------------------------------------
# APP LAYOUT
# -------------------------------------------------------------------------------

app.layout = html.Div(
    [
        dcc.Interval(id='update', n_intervals=0, interval=1000*3),
        get_navbar(),
        #jumbotron,
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(card_temperature, lg=3, sm=12),
                        dbc.Col(card_humidity, lg=3, sm=12),
                        dbc.Col(card_air, lg=3, sm=12),
                        dbc.Col(card_plant, lg=3, sm=12)
                    ], style={"margin-bottom": "24px"}
                ),

                dbc.Row(
                    [
                        dbc.Col(card_infocard_figure, lg=6, sm=12),
                        dbc.Col(card_soil_moisture, lg=6, sm=12)
                    ], style={"margin-bottom": "24px"}
                ),
                
                dbc.Row(
                    [
                        dbc.Col(card_light, lg=4, sm=12),
                        dbc.Col(card_irrigation, lg=4, sm=12),
                    ], style={"margin-bottom": "24px"}
                )
                
            ], id="mainContainer",style={"display": "flex", "flex-direction": "column"}
        ),

        html.P("2021 | Developed by Tolgahan Çepel", className="footer")
    ],
)




# Light On
@app.callback(
    Output('hidden-div', 'children'),
    [
        Input('btn-light-on', 'n_clicks'),
    ]
)

def publish_light_on_mqtt(n_clicks):
    
    if(n_clicks != None):
        client = mqtt.Client()
        client.connect("mqtt.eclipseprojects.io", 1883, 60)
        client.publish("topic/natikay", "l1")
        client.disconnect()



# Light Off
@app.callback(
    Output('hidden-div2', 'children'),
    [
        Input('btn-light-off', 'n_clicks'),
    ]
)

def publish_light_off_mqtt(n_clicks):
    
    if(n_clicks != None):    
        client = mqtt.Client()
        client.connect("mqtt.eclipseprojects.io", 1883, 60)
        client.publish("topic/natikay", "l0")
        client.disconnect()

@app.callback(
    Output('img-light', 'children'),
    [
        Input('update', 'n_intervals')
    ]
)

def update_light_image(timer):
    return html.Img(src=app.get_asset_url(light_img_url), className="img-light"),





# ---------------------------------------------------------------------------------
# Line Charts Callbacks
# ---------------------------------------------------------------------------------

@app.callback(
    [
        Output('graph-infocard-history', 'figure'),
        Output('infocard-style', 'style'),
        Output('graph-soil-moisture-history', 'figure'),
    ],
    
    [
        Input('update', 'n_intervals'),
        Input('select-info', 'value')
    ]
)

def update_soil_moisture(timer, selected_value):
    
    title = 'Main Source for News'
    labels = ['Television', 'Newspaper', 'Internet', 'Radio']
    colors = ['rgb(67,67,67)', 'rgb(115,115,115)', 'rgb(49,130,189)', 'rgb(189,189,189)']

    mode_size = [8, 8, 12, 8]
    line_size = [2, 2, 4, 2]

    x_data = np.vstack((np.arange(2001, 2014),)*4)

    y_data = np.array([
        [74, 82, 80, 74, 73, 72, 74, 70, 70, 66, 66, 69],
        [45, 42, 50, 46, 36, 36, 34, 35, 32, 31, 31, 28],
        [13, 14, 20, 24, 20, 24, 24, 40, 35, 41, 43, 50],
        [18, 21, 18, 21, 16, 14, 13, 18, 17, 16, 19, 23],
    ])

    layout_count = layout.copy()

    # Infocard Figure
    fig_infocard = go.Figure()

    fig_infocard.update_layout(layout_count)

    if(selected_value == "temperature"):
        infocard_style = {'background-color': '#b4af67'}
        infocard_marker_color = "#b4af67"
        infocard_ylabel = "Temperature (°C)"

    elif(selected_value == "humidity"):
        infocard_style = {'background-color': '#009688'}
        infocard_marker_color = "#009688"
        infocard_ylabel = "Humidity (%)"

    fig_infocard.add_trace(go.Scatter(x=x_data[2], y=y_data[2], mode='lines+markers', marker_size=8,
            name=labels[2],
            line=dict(color=infocard_marker_color, width=line_size[2]),
            connectgaps=True,
        )
    )

    # fig_infocard.add_trace(go.Scatter(
    #         x=[x_data[2][0], x_data[2][-1]],
    #         y=[y_data[2][0], y_data[2][-1]],
    #         mode='markers',
    #         marker=dict(color=infocard_marker_color, size=mode_size[2])
    #     )
    # )

    fig_infocard.update_layout(
        title = "",
        xaxis_title="Time",
        yaxis_title=infocard_ylabel,
        xaxis=dict(
            #showticklabels=False
        ),
        showlegend=False
    )

    # Soil Moisture Figure

    fig_soil_moisture = go.Figure()

    
    fig_soil_moisture.update_layout(layout_count)

    for i in range(0, 4):
        fig_soil_moisture.add_trace(go.Scatter(x=x_data[i], y=y_data[i], mode='lines',
            name=labels[i],
            line=dict(color=colors[i], width=line_size[i]),
            connectgaps=True,
        ))

        # endpoints
        fig_soil_moisture.add_trace(go.Scatter(
            x=[x_data[i][0], x_data[i][-1]],
            y=[y_data[i][0], y_data[i][-1]],
            mode='markers',
            marker=dict(color=colors[i], size=mode_size[i])
        ))

    fig_soil_moisture.update_layout(
        title = "",
        xaxis_title="Time",
        yaxis_title="Soil Moisture (%)",
        xaxis=dict(
            #showticklabels=False
        ),
        showlegend=False
    )

    

    
        

    return fig_infocard, infocard_style, fig_soil_moisture



# ---------------------------------------------------------------------------------
# Irrigation Callbacks
# ---------------------------------------------------------------------------------

# Irrigation On
@app.callback(
    Output('hidden-div3', 'children'),
    [
        Input('btn-irrigation-on', 'n_clicks'),
    ]
)

def publish_irrigation_on_mqtt(n_clicks):
    
    if(n_clicks != None):
        client = mqtt.Client()
        client.connect("mqtt.eclipseprojects.io", 1883, 60)
        client.publish("topic/natikay", "i1")
        client.disconnect()



# Irrigation Off
@app.callback(
    Output('hidden-div4', 'children'),
    [
        Input('btn-irrigation-off', 'n_clicks'),
    ]
)

def publish_irrigation_off_mqtt(n_clicks):
    
    if(n_clicks != None):    
        client = mqtt.Client()
        client.connect("mqtt.eclipseprojects.io", 1883, 60)
        client.publish("topic/natikay", "i0")
        client.disconnect()

@app.callback(
    Output('img-irrigation', 'children'),
    [
        Input('update', 'n_intervals')
    ]
)

def update_irrigation_image(timer):
    return html.Img(src=app.get_asset_url(irrigation_img_url), className="img-light"),



@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)

# we use a callback to toggle the collapse on small screens
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == "__main__":
    app.run_server(debug=False, port=8050)