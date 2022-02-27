# https://www.analyticsvidhya.com/blog/2021/12/stock-market-analysis-with-pandas-datareader-and-plotly-for-beginners/
# https://plotly.com/python/pandas-backend/



import pandas_datareader as data
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import cufflinks as cf

tickers = ['GOOG','AMZN','MSFT','AAPL', 'FB']
data_source = 'yahoo'
start_date = '2016-01-01'
end_date = '2021-11-30'
Google = data.DataReader('GOOG', data_source, start_date, end_date)
Amazon = data.DataReader('AMZN', data_source, start_date, end_date)
Microsoft = data.DataReader('MSFT', data_source, start_date, end_date)
Apple = data.DataReader('AAPL', data_source, start_date, end_date)
Facebook = data.DataReader('FB', data_source, start_date, end_date)

df = pd.concat([Google, Amazon, Microsoft, Apple, Facebook], axis=1, keys=tickers)

print(df.head(3).to_string())
df.columns.names = ['Stock Ticker', 'Stock Info']
print(df.head().to_string())
df.xs(key='GOOG', axis=1, level='Stock Ticker')
px.line(df.xs(key='GOOG', axis=1, level='Stock Ticker')['Close'])

px.line(df.xs(key='GOOG', axis=1, level='Stock Ticker')['Close'], range_x=['2020-01-01','2020-12-31'])

px.line(df.xs(key='Close', axis=1, level='Stock Info')[['GOOG', 'AMZN']])


df.xs(key='Close', axis=1, level='Stock Info').head()
c = df.xs(key='Close', axis=1, level='Stock Info')
c.head()


plt.figure(figsize=(20,10))
fig = px.line(c)
fig.show()

plt.figure(figsize=(20,10))
fig = px.area(c, facet_col='Stock Ticker', facet_col_wrap=3)
fig.show()

fig = px.line(c, range_x=['2020-01-01','2020-12-31'])
fig.show()


plt.figure(figsize=(24,16))
fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['GOOG']['Open'],
                high = df['GOOG']['High'],
                low = df['GOOG']['Low'],
                close = df['GOOG']['Close'])])
fig.update_layout(xaxis_rangeslider_visible=False)
fig.show()

cf.go_offline()
google = df['GOOG'][['Open', 'High', 'Low', 'Close']].loc['2021-01-01':'2021-11-30']
google.iplot(kind='candle')











