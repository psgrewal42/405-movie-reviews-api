from typing import List

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from rss_parser import Parser
from requests import get
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

########### Define a few variables ######
from helpers.rss_utils import convert_feed_to_df

tabtitle = 'Vader News Sentiment'
githublink = 'https://github.com/psgrewal42/405-movie-reviews-api'

########### Initiate the app
external_stylesheets: List[str] = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = tabtitle

########### Layout

app.layout = html.Div(children=[
    html.Datalist(id='list-data', children=[
                                            html.Option(value="https://zapier.com/engine/rss/12262777/pgrewal", label = "Zelensky Tweet RSS"),
                                            html.Option(value="http://feeds.bbci.co.uk/news/rss.xml", label="BBC"),
                                            html.Option(value=
                                                        'http://rss.cnn.com/rss/cnn_topstories.rss', label="CNN Top Stories"),
                                            html.Option(value=
                                                        'https://www.washingtontimes.com/rss/headlines/culture/health/', label = "Wash Post Health"),
                                            html.Option(value=
                                                        'https://www.washingtontimes.com/rss/headlines/culture/technology/', label = "Wash Post Tech"),
                                            html.Option(value=
                                                        'https://www.washingtontimes.com/rss/headlines/opinion/editorials/', label = "Wash Post Editorials")]),
    html.Div([
        html.H3('Enter a RSS Feed or Pick from list'),
        dcc.Input(id="input1", type="text", value="", className='six columns',
                  list='list-data'),
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


def max_value_sentiment(obj):
    sentiment = ''
    mx_val = 0
    for sent in ['neg', 'pos', 'neu']:
        if obj[sent] > mx_val:
            mx_val = obj[sent]
            sentiment = sent
    return sentiment


########## Callbacks

# TMDB API call
@app.callback(Output('output1', 'children'),
              [Input('submit-btn', 'n_clicks')],
              State('input1', 'value'))
def on_click(n_clicks, value):
    if n_clicks == 0 or value == "":
        return ""
    try:
        sanl = SentimentIntensityAnalyzer()
        xml = get(value)
        parser = Parser(xml=xml.content)
        feed = parser.parse()
        df = convert_feed_to_df(feed.feed)
        df['sentiment'] = df.apply(lambda row: max_value_sentiment(sanl.polarity_scores(row['description'])), axis=1)
        df['sentiment_tooltip'] = df.apply(lambda row: str(sanl.polarity_scores(row['description'])), axis=1)
        return dash_table.DataTable(df.drop('sentiment_tooltip', axis=1).to_dict('records'),
                                    [{"name": i, "id": i} for i in df.drop('sentiment_tooltip', axis=1).columns]
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
                                    fill_width=False,
                                    tooltip_data=[
                                        {
                                            column: {'value': row['sentiment_tooltip'], 'type': 'markdown'}
                                            for column, value in row.items() if column == 'sentiment'
                                        } for row in df.to_dict('records')
                                    ],
                                    )
    except:
        return "Unable to parse this feed"


############ Deploy
if __name__ == '__main__':
    app.run_server(debug=True)
