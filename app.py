import dash
import dash_core_components as dcc
import dash_html_components as html

import colorlover as cl
import datetime as dt
import flask
import os
import pandas as pd
from pandas_datareader.data import DataReader
import time

server = flask.Flask('stock-tickers')
app = dash.Dash('stock-tickers', server=server, url_base_pathname='/dash/gallery/stock-tickers/', csrf_protect=False)
server.secret_key = os.environ.get('secret_key', 'secret')

app.scripts.config.serve_locally = False
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-finance-1.28.0.min.js'

colorscale = cl.scales['9']['qual']['Paired']

df_symbol = pd.read_csv('tickers.csv')

app.layout = html.Div([
    html.Div([
        html.H2('Google Finance Explorer',
                style={'display': 'inline',
                       'float': 'left',
                       'font-size': '2.65em',
                       'margin-left': '7px',
                       'font-weight': 'bolder',
                       'font-family': 'Product Sans',
                       'color': "rgba(117, 117, 117, 0.95)",
                       'margin-top': '20px',
                       'margin-bottom': '0'
                       }),
        html.Img(src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe.png?response-content-disposition=inline&X-Amz-Security-Token=AgoGb3JpZ2luEMH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSKAAgFQxpQ07Kx0GLQafcr7VZIAK52fLs%2BDV8GG4IbVjOSnoZuOYd9WN5dtgVlYw%2FEg94pGIuUoD7RhOJpDnwQtliUJAmnDya0Zu6aOzGVn1aG0AagobiW3uvAO93jENDH27NOWbcn21zZW%2BfbXW4OzYf1HLurLNh9YKfyQQz3s6GpmhmQ3aHD31zdz43jggDqjwpPn%2Bf01uQRVj15d012DmK1TIewHq4U%2FJbD0%2FEfnS7Vm1gREGctNgAL2UMR2mZhMOqhFKiues%2BicmZWjDt5R%2Fnrf3LpoD0k3YBdyTgj1XLoKOUIsuuJzTt9GHljO%2BljO%2BEcK0iVjq%2FdUYaZJj%2BlInvoq8gMINxAAGgw2NjE5MjQ4NDIwMDUiDMO08PY4zGHhsujrCirPA8mVCl4iDCEOPFvkiufSAGuPdjr%2Fpt3JL%2Bxb2w%2F%2BCh5Zv0A%2B7jL31Xvqw3Atk12Vbbo%2F33Ro7K%2B3eAvpUovqO7ANVYpj4aLbHDGnb0wPuinqOmkfOeTBjH6zq4EqSWKJQsIlGrSsPciV9aGe%2B%2BYSxexqonr1eJtGMtgai51Dz52QQzxIhUrIrQwQd54WuC%2BxZo%2BATvIk7xX1nevEmm0xcOoPpeNYgvzOgJ89uxLbUdH3rz8QwklVkYZgzP7vipdeq77Jgt68hXvK7pxGjsVTTXJvSM1J4Ly%2BjB%2FEpAn5ZjtkUA3LWc%2Floq2ykau24Jw0QM2O69tz3mX%2BSExgQuN2WDZRkidFHaYoasGaXrNFpd%2FwNxXh3YiOuHgEh0v2d%2FXjfUVjAHglUs%2Bcuh8QankQZL1uGXiJpBOqulW%2BlBF8xe7ZAAbPBbMQT9L5QXboMGqdT1reTpqG6HxTdQoReJTirJ5ic5M3MeyXkeJR10JjjoDlIn8BGVRUgjJlqhqjvOQtnQavBPicXxeVlo%2BFPiocT6QsAgOZZO%2B5HRd6JKuavyPXpmZj5iD0JU5CZETvqP%2F0sROgiPojK8cCNitX9oKVJ20zUpiE17GP%2FC2a2SSapy0wnNT6ygU%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20170706T212420Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAJVTH3IBYXSFANAHA%2F20170706%2Fus-west-1%2Fs3%2Faws4_request&X-Amz-Signature=bedfe24a8d85da54da05457dc640c3059255438ac75aecfdd6af249de166ac3f",
                style={
                    'height': '100px',
                    'float': 'right'
                },
        ),
    ]),
    dcc.Dropdown(
        id='stock-ticker-input',
        options=[{'label': s[0], 'value': s[1]}
                 for s in zip(df_symbol.Company, df_symbol.Symbol)],
        value=['YHOO', 'GOOGL'],
        multi=True
    ),
    html.Div(id='graphs')
], className="container")

def bbands(price, window_size=10, num_of_std=5):
    rolling_mean = price.rolling(window=window_size).mean()
    rolling_std  = price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std*num_of_std)
    lower_band = rolling_mean - (rolling_std*num_of_std)
    return rolling_mean, upper_band, lower_band

@app.callback(
    dash.dependencies.Output('graphs','children'),
    [dash.dependencies.Input('stock-ticker-input', 'value')])
def update_graph(tickers):
    graphs = []
    for i, ticker in enumerate(tickers):
        try:
            df = DataReader(ticker, 'google',
                            dt.datetime(2017, 1, 1),
                            dt.datetime.now())
        except:
            graphs.append(html.H3(
                'Data is not available for {}'.format(ticker),
                style={'marginTop': 20, 'marginBottom': 20}
            ))
            continue

        candlestick = {
            'x': df.index,
            'open': df['Open'],
            'high': df['High'],
            'low': df['Low'],
            'close': df['Close'],
            'type': 'candlestick',
            'name': ticker,
            'legendgroup': ticker,
            'increasing': {'line': {'color': colorscale[0]}},
            'decreasing': {'line': {'color': colorscale[1]}}
        }
        bb_bands = bbands(df.Close)
        bollinger_traces = [{
            'x': df.index, 'y': y,
            'type': 'scatter', 'mode': 'lines',
            'line': {'width': 1, 'color': colorscale[(i*2) % len(colorscale)]},
            'hoverinfo': 'none',
            'legendgroup': ticker,
            'showlegend': True if i == 0 else False,
            'name': '{} - bollinger bands'.format(ticker)
        } for i, y in enumerate(bb_bands)]
        graphs.append(dcc.Graph(
            id=ticker,
            figure={
                'data': [candlestick] + bollinger_traces,
                'layout': {
                    'margin': {'b': 0, 'r': 10, 'l': 60, 't': 0},
                    'legend': {'x': 0}
                }
            }
        ))

    return graphs


external_css = ["https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/2cc54b8c03f4126569a3440aae611bbef1d7a5dd/stylesheet.css"]

for css in external_css:
    app.css.append_css({"external_url": css})


if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })


if __name__ == '__main__':
    app.run_server(debug=True)
