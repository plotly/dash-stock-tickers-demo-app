import dash
import dash_core_components as dcc
import dash_html_components as html

import colorlover as cl
import datetime as dt
import finsymbols
import flask
import pandas as pd
from pandas_datareader.data import DataReader
import time

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

colorscale = cl.scales['9']['qual']['Paired']

df_symbol = pd.read_csv('tickers.csv')

app.layout = html.Div([
    html.H2('Google Finance Explorer'),
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
                    'margin': {'b': 0, 'r': 60, 'l': 20, 't': 0},
                    'legend': {'x': 0}
                }
            }
        ))

    return graphs

app.css.append_css({
    'external_url': (
        'https://codepen.io/chriddyp/pen/yXaGgK.css?timestamp=' + str(int(time.time())),
    )
})

if __name__ == '__main__':
    app.run_server(debug=True)
