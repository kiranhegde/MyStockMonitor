# https://towardsdatascience.com/downloading-stock-data-and-representing-it-visually-6433f7938f98
# https://github.com/hmix13/YFinance/blob/master/YahooFinance.ipynb


import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import plotly.express as px
import mplfinance as mpf
# importing Library
import yfinance as yf
import plotly.graph_objects as go

import plotly.express as px

symbol = 'DMART.NS'
start_date = datetime(2019, 1, 1)
end_date = datetime(2022, 1, 4)
df = yf.download(symbol, start=start_date, end=end_date)
# df = pd.DataFrame(pd.read_csv("JSW.csv"))
df.reset_index(inplace=True)
print(df.head().to_string())
for i in ['Open', 'Close', 'High', 'Low']:
    df[i] = df[i].astype('float64')

set1 = {
    'x': df.Date,
    'open': df.Open,
    'close': df.Close,
    'high': df.High,
    'low': df.Low,
    'type': 'candlestick',
}

# finding the moving average of 20 periods
avg_20 = df.Close.rolling(window=20, min_periods=1).mean()

# finding the moving average of 50 periods
avg_50 = df.Close.rolling(window=50, min_periods=1).mean()

# finding the moving average of 50 periods
avg_100 = df.Close.rolling(window=100, min_periods=1).mean()

# finding the moving average of 200 periods
avg_200 = df.Close.rolling(window=200, min_periods=1).mean()

set2 = {
    'x': df.Date,
    'y': avg_20,
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 2,
        'color': 'blue'
    },
    'name': 'Moving Average of 20 periods'
}

set3 = {
    'x': df.Date,
    'y': avg_50,
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 2,
        'color': 'red'
    },
    'name': 'Moving Average of 50 periods'
}
set4 = {
    'x': df.Date,
    'y': avg_100,
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 2,
        'color': 'green'
    },
    'name': 'Moving Average of 100 periods'
}

set5 = {
    'x': df.Date,
    'y': avg_200,
    'type': 'scatter',
    'mode': 'lines',
    'line': {
        'width': 2,
        'color': 'black'
    },
    'name': 'Moving Average of 200 periods'
}

data = [set1, set2, set3, set4, set5]
# Config graph layout
layout = go.Layout({
    'title': {
        'text': symbol,
        'font': {
            'size': 25
        }
    }
})
fig = go.Figure(data=data, layout=layout)
fig.show()
