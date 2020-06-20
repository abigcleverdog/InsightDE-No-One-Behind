import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go

import os, time
import random
import pandas as pd
import numpy as np
from collections import deque

import mysql.connector as con
from mysql.connector import errorcode
import json, datetime


# establish connection to database
cnx = con.connect(host = '<localhost or host address>', user='<user name>', password='<password>', database='<database name>')
print("***---***"*3, "db connected!")

# load default dataset
mycursor = cnx.cursor()

exe = '''SELECT * from {} '''.format('202006_17162609')
        
mycursor.execute(exe)

query_res = mycursor.fetchall()

mycursor.close()

cnx.close()

# initiate time series data
ts = [[0],[0],[0]]

# selected datasets
dropdown_options = [
            {'label': '10 m5.large feeders', 'value': '202006_17162609'},
            {'label': '5 m5.large feeders', 'value': '202006_18010830'},
            {'label': '3 m5.large feeders', 'value': '202006_18010235'},
            {'label': '2 m5.24xlarge feeders', 'value': '202006_19164148'},
            {'label': '1/5/10/20 providers and 1 analyzer', 'value': '2020_06_18_07_42_14'},
            {'label': '1/5/10/20 providers and 5 analyzer', 'value': '2020_06_18_08_04_20'},
            {'label': '1/5/10/20 providers and 10 analyzer', 'value': '2020_06_18_08_15_55'},
            {'label': '1/5/10/20 providers and 20 analyzer', 'value': '2020_06_18_08_26_06'},
            {'label': '1/5/10/20 providers and 1+1 analyzer', 'value': '2020_06_18_08_40_57'},
            {'label': '1/5/10/20 providers and 5+5 analyzer', 'value': '2020_06_18_08_49_36'},
            {'label': '1/5/10/20 providers and 10+10 analyzer', 'value': '2020_06_18_08_57_10'},
            {'label': '1/5/10/20 providers and 20+20 analyzer', 'value': '2020_06_18_09_04_29'},
            {'label': '2*providers and 1+1 analyzer', 'value': '2020_06_18_09_14_47'},
            {'label': '2*providers and 5+5 analyzer', 'value': '2020_06_18_09_20_54'},
            {'label': '2*providers and 10+10 analyzer', 'value': '2020_06_18_09_32_11'},
            {'label': '2*providers and 20+20 analyzer', 'value': '2020_06_18_09_39_25'},
            {'label': '5*providers and 1+1 analyzer', 'value': '2020_06_18_09_49_53'},
            {'label': '5*providers and 5+5 analyzer', 'value': '2020_06_18_09_59_22'},
            {'label': '5*providers and 10+10 analyzer', 'value': '2020_06_18_10_08_56'},
            {'label': '5*providers and 20+20 analyzer', 'value': '2020_06_18_10_19_09'},
        ]

def select_table(value):
    """ choose a dataset to display """
    # establish connection to database
    cnx = con.connect(host = '<localhost or host address>', user='<user name>', password='<password>', database='<database name>')
    print("***---***"*3, "db connected!")

    mycursor = cnx.cursor()

    exe = '''SELECT * from {} '''.format(value)
            
    mycursor.execute(exe)

    # update app dataset
    global query_res, ts
    query_res = mycursor.fetchall()

    mycursor.close()

    cnx.close()

    # initiate time series data
    ts = [[0],[0],[0]]
    
def update_message(num):
    """ read another row from current dataset """
    num = num % len(query_res)
    return query_res[num]

def build_df(outcome):
    """ formate the message for display """
    df = pd.DataFrame(list(outcome.items()), columns = ['cameras','attention'])
    return df
    
def build_mat(df):
    """ format data for heatmap """
    row = int(len(df)**.5)
    trim = len(df) % row
    
    z = df['attention'].tolist()
    labels = df['cameras'].tolist()
    
    z = z[0:len(z)-trim]
    labels = labels[0:len(labels)-trim]
    z = [int(_) for _ in z]

    z = np.reshape(z, (row,len(df)//row))
    labels = np.reshape(labels, (row,len(df)//row))
    
    return z, labels



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div(
    id='app-container',
    children=[
        dcc.Interval(
                id='my_interval',
                disabled=True,      # if True, the counter will no longer update
                interval=1*1000,    # increment the counter n_intervals every interval milliseconds
                n_intervals=0,      # number of times the interval has passed
                max_intervals=-1,   # number of times the interval will be fired.
                                    # if -1, then the interval has no limit (the default)
                                    # and if 0 then the interval stops running.
        ),

        #Banner
        html.Div( 
            id='banner',
            className='banner',
            children=[
                html.Div(
                    dcc.Dropdown(
                        id='my-dropdown',
                        options=dropdown_options,
                        value='202006_17162609',
                        clearable=False,
                        style={'width':700,}
                    ), 
                    style={'font-size':16, 'display':'inline'}
                ),     
                html.Div([html.Button('Start/Stop', id="start_btn",n_clicks=0)], style={'font-size':24, 'display':'inline'}),    
            
                
                html.Div(id='output_data', style={'font-size':24, 'display':'inline', 'padding-left': '50px'}),
            ] 
        ),
        html.Div([
            # Left column
            html.Div([
                dcc.Graph(id="mypiechart", style={"height": "100%", "width": "100%"}),
                dcc.Graph(id="mylinechart", style={"height": "100%", "width": "100%"}),
                dcc.Graph(id="mylinechart2", style={"height": "100%", "width": "100%"}),
                
            
            ], className="four columns",
            style={'align-items': 'center', 'justify-content': 'center'} ),

            # Right column
            html.Div([
                # html.B('Heatmap'),
                # html.Hr(),
                dcc.Graph(id='myheatmap'),
            ], className="eight columns"),
        ], className="row")
])


@app.callback(
    [Output('start_btn', 'n_clicks'),
     Output('my_interval', 'n_intervals'),],
    [Input('my-dropdown', 'value')])
def update_output(value):
    """ switch dataset, reinitiate start button and interval """
    select_table(value)
    return [0, 0]


@app.callback(
    [Output('output_data', 'children'),
     Output('mypiechart', 'figure'),
     Output('mylinechart', 'figure'),
     Output('mylinechart2', 'figure'),
     Output('myheatmap', 'figure')],
    [Input('my_interval', 'n_intervals'),
     ]
)
def update_graph(num):
    """ update content on the page """
    if num==0:
        raise PreventUpdate
    else:
        print('\n update_graphs \n')
        
        # load new row from the dataset
        ndf = update_message(num-1)
        
        # parse the row
        _, total_cam, timestamp, delay, outcome = ndf
        outcome = json.loads(outcome)
        
        df = build_df(outcome)
        
        total_att = df['attention'].sum()
        
        # update time series data
        ts[0].append(ts[0][-1] + 1)
        ts[1].append(total_att/total_cam * 100)
        ts[2].append(delay)
        
        
        # pie chart
        attentions = pd.DataFrame({'label':['attention','noattention'], 'counts': [0,0]})
        attentions.iloc[0,1] = total_att
        attentions.iloc[1,1] = total_cam - total_att
        
        fig = px.pie(
            data_frame = attentions,
            values = 'counts',
            names = 'label',
            hole = 0.1,
            width = 380,
            height = 200,
        )
        fig.update_layout(
            margin=dict(l=30, r=10, t=10, b=10),
        )
        
        # over time plots
        tss = ts
        
        fig2={
            'data': [
                {
                    'x': tss[0], 
                    'y': tss[1], 
                    'type': 'line', 
                    'name': 'Att over time',
                }
            ],
            
            'layout': {
                'title': 'Attention over time (%)',
                'width': 380,
                'height': 170, 
                'margin': {'l':30,
                    'r':10,
                    't':25,
                    'b':20,
                },
            }
        }
        
        fig2_2={
            'data': [
                {
                    'x': tss[0], 
                    'y': tss[2], 
                    'type': 'line', 
                    'name': 'Delay over time',
                }
            ],
            
            'layout': {
                'title': 'Delay over time (s)',
                'width': 380,
                'height': 130, 
                'margin': {'l':30,
                    'r':10,
                    't':25,
                    'b':20,
                },
            }
        }
        
        # heatmap plot
        hm_z, hm_labels = build_mat(df)
        
        fig3 ={
            'data': [{
                'z': hm_z,
                'text': hm_labels,
                'type': 'heatmap',
                'showscale': False,
                'colorscale': [[0, "#ef553b"], [1, "#636efa"]],
            }],
            'layout':  {
                'margin': dict(l=70, b=50, t=50, r=50),
                'height': 490,
                'annotations': hm_labels,
            }
        }

    return ("total attention is : {} out of {};   Delay: {} seconds".format(total_att, total_cam, delay), 
        fig, 
        fig2, 
        fig2_2, 
        fig3)



@app.callback(
    Output('my_interval', 'disabled'),
    [Input('start_btn', 'n_clicks')]
)
def stop_interval(n_clicks):
    """ toggle start/stop displaying """
    return not bool(n_clicks & 1)


server = app.server

if __name__ == '__main__':
    app.run_server(debug=True, host='<host>', port=80)

