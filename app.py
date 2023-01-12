from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import pickle

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', 'https://codepen.io/chriddyp/pen/brPBPO.css']
color_continuous_scale = 'Turbo' #'RdBu_r'

app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# load data
with open('counties.pickle', 'rb') as infile:
    counties = pickle.load(infile)
data = pd.read_pickle('data.pickle')

fig = px.choropleth(data, 
                    geojson=counties, 
                    locations='fips', 
                    color='ok',
                    color_continuous_scale=color_continuous_scale,
                    range_color=(100000, 1500000),
                    scope="usa",
                    labels={'ok':'House price', 
                            'county':'County'},
                    hover_name="county",
                    hover_data=[
                        "Average annual low (°F)", 
                        "Average annual high (°F)",
                        "Average temp, coldest month (°F)",
                        "Average temp, hottest month (°F)",
                        "Average monthly precipitation (inches)",
                        "Total annual precipitation (inches)"
                        ]                        
                    )

fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

app.layout = html.Div(children=[
    html.H1(children='Where to buy a house?'),

    html.Div(children='''
        
    '''),
    html.Div([html.Button('Change unit', id='change_unit', n_clicks=0),
              html.Button('Update', id='update', n_clicks=0)]),
    
    dcc.Graph(
        id='us_map',
        figure=fig
    ),

    html.Label('Maximum typical house cost'),
    dcc.Slider(
        id='house_price',
        min=30000,
        max=1500000,
        marks={n:'${0:,}'.format(n) for n in range(100000,1500000,100000)},
        value=400000,
    ),

    html.Label('Monthly low / high temperature'),
    html.Div([dcc.RangeSlider(-10, 100,
                              id='monthly_high_low',
                              value=[20, 80], 
                              marks={n:'{0}°F'.format(n) for n in range(-10, 101, 5)},
                              allowCross=False,
                              tooltip={"placement": "bottom", "always_visible": True})
              ], id='monthly_high_low_container'),
    
    html.Label('Annual extreme temperatures'),
    html.Div([dcc.RangeSlider(-10, 100,
                              id='annual_high_low',
                              value=[-10, 100], 
                              marks={n:'{0}°F'.format(n) for n in range(-10, 101, 5)},
                              allowCross=False,
                              tooltip={"placement": "bottom", "always_visible": True})
              ], id='annual_high_low_container'),
])

@app.callback(
    Output(component_id='us_map', component_property= 'figure'),
    [Input('update', 'n_clicks')],
    [State('monthly_high_low', 'value'),
           State('annual_high_low', 'value'),
           State('house_price', 'value')])
def update_figure(n_clicks,
                  monthly_high_low, 
                  annual_high_low,
                  house_price):
    
    data['ok'] = data['house_price']
    data.loc[(data['min_tmp_year'] < annual_high_low[0]) |
             (data['min_avg_tmp_year'] < monthly_high_low[0]) |
             (data['max_tmp_year'] > annual_high_low[1]) |
             (data['max_avg_tmp_year'] > monthly_high_low[1]) |
             (data['house_price'] > house_price),
             'ok'] = None

    fig = px.choropleth(data, 
                        geojson=counties, 
                        locations='fips', 
                        color='ok',
                        color_continuous_scale=color_continuous_scale,
                        range_color=(100000, 1500000),
                        scope="usa",
                        labels={'ok':'House price', 
                                'county':'County'},
                        hover_name="county",
                        hover_data=[
                            "Average annual low (°F)", 
                            "Average annual high (°F)",
                            "Average temp, coldest month (°F)",
                            "Average temp, hottest month (°F)",
                            "Average monthly precipitation (inches)",
                            "Total annual precipitation (inches)"
                            ]                        
                        )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig
    


@app.callback(
    [Output('monthly_high_low_container', 'children'),
     Output('annual_high_low_container', 'children'),],
    [Input('change_unit', 'n_clicks'),
     Input(component_id='monthly_high_low', component_property='value'),
     Input(component_id='annual_high_low', component_property='value'),]
)
def displayClick(change_unit, monthly_high_low, annual_high_low):
    
    def to_celsius(x):
        return int((x - 32) * 5 / 9)
    
    if change_unit % 2 == 1:
        return [html.Div([dcc.RangeSlider(-10, 100,
                                          id='monthly_high_low',
                                          value=[monthly_high_low[0], monthly_high_low[1]], 
                                          marks={n:'{0}°C'.format(to_celsius(n)) for n in range(-10, 101, 5)},
                                          allowCross=False,
                                          #tooltip={"placement": "bottom", "always_visible": True}
                                          )], id='monthly_high_low_container'),
                html.Div([dcc.RangeSlider(-10, 100,
                                          id='annual_high_low',
                                          value=[annual_high_low[0], annual_high_low[1]], 
                                          marks={n:'{0}°C'.format(to_celsius(n)) for n in range(-10, 101, 5)},
                                          allowCross=False,
                                          #tooltip={"placement": "bottom", "always_visible": True}
                                          )], id='annual_high_low_container')]
    
    else:
        return [html.Div([dcc.RangeSlider(-10, 100,
                                          id='monthly_high_low',
                                          value=[monthly_high_low[0], monthly_high_low[1]],
                                          marks={n:'{0}°F'.format(n) for n in range(-10, 101, 5)},
                                          allowCross=False,
                                          tooltip={"placement": "bottom", "always_visible": True}
                                          )], id='monthly_high_low_container'),
                html.Div([dcc.RangeSlider(-10, 100,
                                          id='annual_high_low',
                                          value=[annual_high_low[0], annual_high_low[1]], 
                                          marks={n:'{0}°F'.format(n) for n in range(-10, 101, 5)},
                                          allowCross=False,
                                          tooltip={"placement": "bottom", "always_visible": True}
                                          )], id='annual_high_low_container')]

if __name__ == '__main__':
    app.run_server(debug=False)