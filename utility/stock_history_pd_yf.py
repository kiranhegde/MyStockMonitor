# https://towardsdatascience.com/downloading-stock-data-and-representing-it-visually-6433f7938f98
# https://github.com/hmix13/YFinance/blob/master/YahooFinance.ipynb

import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import plotly.express as px
import mplfinance as mpf
#importing Library
import yfinance as yf



start_date = datetime(2019, 1, 1)
end_date = datetime(2022, 1, 4)
data = yf.download('DMART.NS', start=start_date, end=end_date)
mpf.plot(data,type='candle',mav=(20,50,100),volume=True,show_nontrading=True)

exit()

#setting the ticker
hindpetro = yf.Ticker("HINDPETRO.NS")
#Display stock information
print(hindpetro.info)
# Dsiplay all the actions taken in the lifetime of the stock i.e    # dividends and splits with the dates when they are provided
print(hindpetro.actions)

#Display Dividends
print(hindpetro.dividends)
#Display Splits
print(hindpetro.splits)

df = hindpetro.history(period="max")
print(df.to_string())

#Reseting the index
df = df.reset_index()
#Converting the datatype to float
for i in ['Open', 'High', 'Close', 'Low']:
    df[i] = df[i].astype('float64')

# Creating Line chart using Plotly Graph_objects with Range slider and button
fig = go.Figure([go.Scatter(x=df['Date'], y=df['High'])])
fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1m", step="month",
                 stepmode="backward"),
            dict(count=6, label="6m", step="month",
                 stepmode="backward"),
            dict(count=1, label="YTD", step="year",
                 stepmode="todate"),
            dict(count=1, label="1y", step="year",
                 stepmode="backward"),
            dict(step="all")
        ])
    )
)
fig.show()

# Creating candlestick chart with range slider
fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])

fig.show()

# Creating OHLC Chart
fig = go.Figure(data=go.Ohlc(x=df['Date'],
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close']))
fig.show()

fig = go.Figure(go.Indicator(
    domain = {'x': [0, 1], 'y': [0, 1]},
    value = 450,
    mode = "gauge+number+delta",
    title = {'text': "Speed"},
    delta = {'reference': 380},
    gauge = {'axis': {'range': [None, 500]},
             'steps' : [
                 {'range': [0, 250], 'color': "lightgray"},
                 {'range': [250, 400], 'color': "gray"}],
             'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 490}}))

fig.show()



fig = px.area( x=df["Date"], y=df["High"])
fig.show()











