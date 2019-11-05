# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 10:59:17 2019

@author: zhli
"""
import os
os.chdir('C:\\Users\\zhli\\Desktop\\sql automation\\EWR')


import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import EWR
import da_location
import base64
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input,Output
from dash.exceptions import PreventUpdate

type_list,table=EWR.retrieveEWR()
da_location_list=da_location.get_location_delivery_agent()


###################intializing functions##################
def type_title_with_numbers(da,filter_type,dataframe):
    number=len(dataframe[(dataframe["Delivery Agent"]==da) & (dataframe["EWR type"]==filter_type)].index)
    return filter_type+" ("+str(number)+")"

logo_file='logo.png'
encoded_image=base64.b64encode(open(logo_file,'rb').read())




app = dash.Dash(__name__)

mapbox_access_token = "pk.eyJ1IjoiemhsaTE5OTIiLCJhIjoiY2syMjgyYnRzMGpubzNubzVkbms1bXFrNCJ9.lf0eMIAK8OLvUHVcqqOi-g"
px.set_map_acess_toekn=(mapbox_access_token)

app.layout = html.Div(
            children=[
                    html.Div(
                            className="row",
                            children=[
                                    html.Div(
                                            className="logo & main control panel",
                                            children=[
                                                    html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode())
                                                            ),
                                                    html.P(
                                                            """Initate the report by selecting your region and delivery agent"""
                                                            ),
                                                    html.Div(id='regional filter',
                                                                children=dcc.Dropdown(id='region_filter',
                                                                                      options=[{
                                                                                              'label': region,
                                                                                              'value': region}
                                                                                               for region in table['Region'].unique()]
                                                                                               ),
                                                                                               style={'display': 'inline-block', 'width': '30%', 'margin-left': '7%'}),
                                                    html.Div(id='delivery agent filter',
                                                                children=dcc.Dropdown(id='da_filter',
                                                                                      options=[{
                                                                                              'label': da,
                                                                                              'value': da}
                                                                                               for da in table["Delivery Agent"].unique()]
                                                                                               ),
                                                                                      style={'display': 'inline-block', 'width': '30%', 'margin-left': '7%'}),
                                                    html.Div(id='ewr type filter',
                                                                children=dcc.Dropdown(id='type_filter',
                                                                                      options=[{
                                                                                              'label': ewr_type,
                                                                                              'value': ewr_type}
                                                                                               for ewr_type in type_list]
                                                                                               ),
                                                                                       style={'display': 'inline-block', 'width': '30%', 'margin-left': '7%'}),
                                                    html.Div(id='map',
                                                            children=[dcc.Graph(id='map-graph')],),
                                 html.Div(
                                    className="main_table_panel",
                                    children=[
                                            dash_table.DataTable(id='table',
                                                                 columns=[{"name":x,"id":x} for x in ["Order ID","Reservation Key","Customer Name","Service Level","Delivery Date","Product Description","Total Weight","Total Carton Count","Extranet Status","Stop type","Delivery Agent","Region"]],
                                                                 style_cell={'maxWidth': '500px', 'whiteSpace': 'normal','textAlign':'center','backgroupcolor':'#ffb3ff'},
                                                                 style_table={'overflowX':'scroll','Width':'1500px','maxHeight':'300'},
                                                                 fixed_rows={'headers':True,'data':0},
                                                                 row_deletable=True,
                                                                 data=table.to_dict("rows"),
                                                                 row_selectable="multi",
                                                                 page_size=30,
                                                                 page_current=0,
                                                                 sort_action="native",
                                                                 sort_mode="multi",
                                                                 style_as_list_view=True)
                                            #dash_Checklist(
                                                    #options=[])
                                                    ]
                                            ),
                                    ]),
                ],style={'columnCount':2}
)])

@app.callback(Output('da_filter','options'),
        [Input('region_filter','value')])
def region_da_dependency(region):
    da=table[table['Region']==region]["Delivery Agent"].unique()
    return [{'label': i, 'value': i} for i in da]

@app.callback([Output('type_filter','options'),Output('map-graph','figure')],
              [Input('da_filter','value')])
def options_with_num(da):
    available_type=table[table['Delivery Agent']==da]["EWR type"].unique()
    zoom=2.46
    latInitial=42.6866567
    lonInitial=-101.385506
    bearing=0
    size=8
    if da:
        zoom=11
        size=15
        latInitial=da_location_list[da]["lat"]
        lonInitial=da_location_list[da]["lon"]
    updated_map=go.Figure(
            data=[go.Scattermapbox(
                    lat=[da_location_list[i]["lat"] for i in da_location_list],
                    lon=[da_location_list[i]["lon"] for i in da_location_list],
                    mode="markers",
                    hoverinfo="text",
                    hovertext=[i for i in da_location_list],
                    marker=dict(size=size,color="#8C11E7"),)
                    ],
            layout=go.Layout(
                    autosize=True,
                    margin=go.layout.Margin(l=0,r=0,t=0,b=0),
                    showlegend=False,
                    mapbox=dict(
                            accesstoken=mapbox_access_token,
                            center=dict(lat=latInitial,lon=lonInitial),
                            style="light",
                            bearing=bearing,
                            zoom=zoom,
                    )))
    return [{'label': type_title_with_numbers(da=da,filter_type=i,dataframe=table), 'value': i} for i in available_type],updated_map

    
@app.callback(Output('table', 'data'),
              [Input('type_filter', 'value'),Input('da_filter','value')])
def main_table_filter(ewr_type,da):
    if ewr_type and da:
        return table[(table["Delivery Agent"]==da) & (table["EWR type"]==ewr_type)].to_dict("rows")
    else:
        raise PreventUpdate
        
#@app.callback(Output('table','columns'),
#              [Input('type_filter','value')])
#def column_filter(ewr_type):
#    if ewr_type=="VIP+/Perigold Order":
#       
#    if ewr_type=="Release Pending":
        


app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
if __name__ == "__main__":
    app.run_server(debug=True,use_reloader=False)
    
    
