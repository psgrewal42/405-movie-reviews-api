import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from rss_parser import Parser
from requests import get
import json

########### Define a few variables ######
from helpers.rss_utils import convert_feed_to_df

tabtitle = 'Vader News Sentiment'
githublink = 'https://github.com/austinlasseter/tmdb-rf-classifier'



########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

########### Layout

app.layout = html.Div(children=[
    html.Div([
        html.H3('Enter a RSS Feed'),
        dcc.Input(id="input1", type="text", value="http://feeds.bbci.co.uk/news/rss.xml", className='six columns'),
        html.Button('Submit', id='submit-btn', n_clicks=0, style={'marginLeft': '20px'}),
        html.Br(),
        html.Br(),
        html.Div(id="output1", children=[], className="nine columns")
    ], className='twelve columns'),


        # Output
    html.Div([
        # Footer
        html.Br(),
        html.A('Code on Github', href=githublink, target="_blank")
    ], className='twelve columns'),
    ]
)

########## Callbacks

# TMDB API call
@app.callback(Output('output1', 'children'),
              [Input('submit-btn', 'n_clicks')],
              State('input1', 'value'))
def on_click(n_clicks, value):
    xml = get(value)
    parser = Parser(xml=xml.content)
    feed = parser.parse()
    df = convert_feed_to_df(feed.feed)
    return dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]
                                , style_table={
                                    'overflowY': 'scroll',
                                    'overflowX': 'auto',
                                    'width': 'auto'
                                },
                                style_cell={
                                    'textAlign': 'left',
                                    'minWidth': '150px',
                                    'width': '500px',
                                    'maxWidth': '600px',
                                    'whiteSpace': 'normal'

                                },
                                style_header={
                                    'textAlign': 'center',
                                    'fontWeight': 'bold'
                                },
                                page_size=10,
                                fill_width=False
                                )



############ Deploy
if __name__ == '__main__':
    app.run_server(debug=True)
