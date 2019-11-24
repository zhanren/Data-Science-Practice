# -*- coding: utf-8 -*-
"""
Created on Sat Nov  2 19:21:21 2019

@author: Brandon
"""



import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input,Output
from dash.exceptions import PreventUpdate
import get_zomato_data

database=get_zomato_data.get_zomato_full_list()

app = dash.Dash(__name__)

mapbox_access_token = "pk.eyJ1IjoiemhhbnJlbiIsImEiOiJjazJpOTI2Mm8xZTYzM2luMGc0ajMxMm5mIn0.LxO9GQw6M6RUJCBwOm8csg"
px.set_map_acess_toekn=(mapbox_access_token)

app.layout = html.Div(
            children=[
                    html.Div(
                            className="column",
                            children=[
                                    html.Div(
                                            className="logo & main control panel",
                                            children=[
                                                    html.Img(),
                                                    html.P(),
                                                    html.Div(id='filter',
                                                             children=dcc.Dropdown(id='test',
                                                                                   options=[{'label':'',
                                                                                           'value':''}]                                                                              
                                                                                           )),
                    html.Div(className="main_map",
                             children=[dcc.Graph(id='map-graph',
                                                 figure=go.Figure(
                                                         data=[go.Scattermapbox(
                                                                 lat=[i for i in database["restaurant.location.latitude"].astype(float)],
                                                                 lon=[i for i in database["restaurant.location.longitude"].astype(float)],
                                                                 mode="markers",
                                                                 hoverinfo="text",
                                                                 hovertext=[{"Name:{} <br> Style:{} <br> Location:{}".format(name,style,location)} for name,style,location in zip(database["restaurant.name"],database["restaurant.cuisines"],database["restaurant.location.address"])],
                                                                 marker=dict(size=8,color="#8C11E7"),)],
                                                         layout=go.Layout(
                                                                 autosize=True,
                                                                 margin=go.layout.Margin(l=0,r=0,t=0,b=0),
                                                                 showlegend=False,
                                                                 mapbox=dict(
                                                                         accesstoken=mapbox_access_token,
                                                                         center=dict(lat=database["restaurant.location.latitude"].astype(float).mean(),
                                                                                     lon=database["restaurant.location.longitude"].astype(float).mean()),
                                                                         style="light",
                                                                         bearing=0,
                                                                         zoom=13,
                    ))))])])
])])

@app.callback(Output('map-graph','figure'),
              [Input('map-graph','figure')])
def zoom_control(figure):
    zoom=figure["layout"]["mapbox"]["zoom"]
    return figure.update_figure(marker=dict(size=8+(zoom-13)*0.1,color="#8C11E7"))

#@app.callback(Output('map-graph','figure'),
 #             [Input('test','value')])
#def options_with_num(option):
#    updated_map=
#    return updated_map        

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
if __name__ == "__main__":
    app.run_server(debug=True,use_reloader=False)





