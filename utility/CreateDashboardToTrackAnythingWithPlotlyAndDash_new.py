import pandas as pd
from glob import glob
from time import strftime, sleep
import numpy as np
from datetime import datetime
from pandas_datareader import data as pdr
from pandas.tseries.offsets import BDay
import yfinance as yf
import dash
from dash import dcc
# import dash_core_components as dcc
from dash import html
from dash import dash_table
# import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
from plotly import graph_objs as go
import matplotlib.pyplot as plt
# import dash_table
import plotly.io as pio
import os
from utility.libnames import PATH_TO_DATABASE, PDIR

yf.pdr_override()


# simple function to make headers nicer
def clean_header(df):
    df.columns = df.columns.str.strip().str.lower().str.replace('.', '', regex=True)
    df.columns = df.columns.str.replace('(', '', regex=True).str.replace(')', '', regex=True)
    df.columns = df.columns.str.replace(' ', '_', regex=True).str.replace('_/_', '/', regex=True)


# timestamp for file names
def get_now():
    now = datetime.now().strftime('%Y-%m-%d_%Hh%Mm')
    return now


# E:\SharesAndStocks\MyStockMonitor\utility\inputs\transactions_all
# last_file = glob('inputs/transactions_all/transactions.xlsx')[-1]  # path to file in the folder
last_file = os.path.join(PDIR, 'inputs', 'transactions_all', 'transactions.xlsx')
print("#", last_file[-(len(last_file)) + (last_file.rfind('/') + 1):])
all_transactions = pd.read_excel(last_file)
all_transactions.date = pd.to_datetime(all_transactions.date, format='%d/%m/%Y')
# print(all_transactions.to_string())
# exit()

all_tickers = list(all_transactions['ticker'].unique())
for symbol in all_tickers:
    mask = all_transactions['ticker'] == symbol
    df = all_transactions.loc[mask, ['date', 'ticker', 'type']]
    df = df.sort_values(by='date', ascending=False)
    print(df)
    exit()
exit()
# some tickers may have been delisted. need to blacklist them here
blacklist = ['VSLR', 'HTZ']
filt_tickers = [tick for tick in all_tickers if tick not in blacklist]
print('You traded {} different stocks'.format(len(all_tickers)))

# all transactions without the delisted stocks
final_filtered = all_transactions[~all_transactions.ticker.isin(blacklist)]

# Collecting the price history for all tickers
ly = datetime.today().year - 1
today = datetime.today()
start_sp = datetime(2019, 1, 1)
end_sp = today
start_stocks = datetime(2019, 1, 1)
end_stocks = today
start_ytd = datetime(ly, 12, 31) + BDay(1)

# print(filt_tickers)
# exit()

all_data = pd.DataFrame()


def get(tickers, startdate, enddate):
    ticker = f"{tickers}.NS"

    def data(ticker):
        return (yf.download(ticker, start=startdate, end=enddate))

    datas = map(data, ticker)
    return (pd.concat(datas, keys=tickers, names=['ticker', 'date']))


# all_data = get(filt_tickers, start_stocks, end_stocks)
# filt_tickers = ["AFFLE", "MASTEK"]

for ticker in filt_tickers:
    tick = f"{ticker}.NS"
    # print(tick)
    path_to_csv_file = os.path.join(PDIR, 'outputs', 'price_hist', f'{ticker}_price_hist.csv')
    # path_to_csv_file = 'outputs/price_hist/{}_price_hist.csv'.format(tick)
    if os.path.isfile(path_to_csv_file):
        abc = pd.read_csv(path_to_csv_file)
        abc.set_index('date', inplace=True)
        abc = pd.concat({ticker: abc}, names=['ticker', 'date'])
        all_data = pd.concat([all_data, abc])
    else:
        # abc = get([tick], start_stocks, end_stocks)
        abc = yf.download(tick, start=start_stocks, end=end_stocks)
        abc.reset_index(inplace=True)
        clean_header(abc)
        # abc.reset_index(drop=True, inplace=True)
        # print(abc.head().to_string())
        abc.to_csv(path_to_csv_file, index=False)
        abc = pd.concat({ticker: abc}, names=['ticker', 'date'])
        all_data = pd.concat([all_data, abc])

clean_header(abc)
# saving all stock prices individually to the specified folder
# for tick in filt_tickers:
#     all_data.loc[tick].to_csv('../outputs/price_hist/{}_price_hist.csv'.format(tick))


print(all_data.info())
# exit()
# MEGA_DICT = dictionary with all the tickers as keys, and their ticker prices as DF
# MEGA_DF = all the DF's from DICT, concatenated along the columns. Can use filter to select columns
MEGA_DICT = {}  # you have to create it first
min_date = '2020-06-07'  # optional
TX_COLUMNS = ['date', 'ticker', 'cashflow', 'cml_units', 'cml_cost', 'gain_loss']
tx_filt = all_transactions[TX_COLUMNS]  # keeping just the most relevant ones for now

# filt_tickers = ["AFFLE"]
# print(all_transactions.head().to_string())
# print(all_data.head().to_string())
symbol = "AFFLE"
prices_df = all_data[all_data.index.get_level_values('ticker').isin([symbol])].reset_index()
PX_COLS = ['date', 'adj_close']
prices_df = prices_df[prices_df.date >= min_date][PX_COLS].set_index(['date'])
tx_df = tx_filt[tx_filt.ticker == symbol].groupby('date').agg({'cashflow': 'sum',
                                                               'cml_units': 'last',
                                                               'cml_cost': 'last',
                                                               'gain_loss': 'sum'})
print(tx_df.to_string())
tx_and_prices = pd.merge(prices_df, tx_df, how='outer', left_index=True, right_index=True).fillna(0)
print(prices_df.to_string())
print(tx_and_prices.to_string())

exit()

for ticker in filt_tickers:
    # print("--->", ticker)
    prices_df = all_data[all_data.index.get_level_values('ticker').isin([ticker])].reset_index()
    # print(prices_df.to_string())
    # exit()
    ## Can add more columns like volume!
    PX_COLS = ['date', 'adj_close']
    prices_df = prices_df[prices_df.date >= min_date][PX_COLS].set_index(['date'])
    # Making sure we get sameday transactions
    tx_df = tx_filt[tx_filt.ticker == ticker].groupby('date').agg({'cashflow': 'sum',
                                                                   'cml_units': 'last',
                                                                   'cml_cost': 'last',
                                                                   'gain_loss': 'sum'})
    # Merging price history and transactions dataframe
    tx_and_prices = pd.merge(prices_df, tx_df, how='outer', left_index=True, right_index=True).fillna(0)
    # This is to fill the days that were not in our transaction dataframe
    tx_and_prices['cml_units'] = tx_and_prices['cml_units'].replace(to_replace=0, method='ffill')
    tx_and_prices['cml_cost'] = tx_and_prices['cml_cost'].replace(to_replace=0, method='ffill')
    tx_and_prices['gain_loss'] = tx_and_prices['gain_loss'].replace(to_replace=0, method='ffill')
    # Cumulative sum for the cashflow
    tx_and_prices['cashflow'] = tx_and_prices['cashflow'].cumsum()
    tx_and_prices['avg_price'] = (tx_and_prices['cml_cost'] / tx_and_prices['cml_units'])
    tx_and_prices['mktvalue'] = (tx_and_prices['cml_units'] * tx_and_prices['adj_close'])
    tx_and_prices = tx_and_prices.add_prefix(ticker + '_')
    # Once we're happy with the dataframe, add it to the dictionary
    MEGA_DICT[ticker] = tx_and_prices.round(3)

print(MEGA_DICT['AFFLE'].tail().to_string())
# print(MEGA_DF.info())
path_to_csv_file_mega = os.path.join(PDIR, 'outputs', 'mega', f'MEGA_DF_{get_now()}.csv')
MEGA_DF = pd.concat(MEGA_DICT.values(), axis=1)
MEGA_DF.to_csv(path_to_csv_file_mega)
print(MEGA_DF.info())

# last_file = os.path.join(PDIR, 'outputs', 'mega', f'MEGA_DF_{get_now()}.csv')
# print("last_file", last_file)
last_file = path_to_csv_file_mega
# last_file = glob('outputs/mega/MEGA*.csv')[-1]  # path to file in the folder
print(last_file[-(len(last_file)) + (last_file.rfind('/') + 1):])
MEGA_DF = pd.read_csv(last_file)

MEGA_DF['date'] = pd.to_datetime(MEGA_DF['date'])
MEGA_DF.set_index('date', inplace=True)

# Portfolio DF
portf_allvalues = MEGA_DF.filter(regex='mktvalue').fillna(0)  # getting just the market value of each ticker

portf_allvalues['portf_value'] = portf_allvalues.sum(axis=1)  # summing all market values
# Portfolio gain/loss
portf_gain_loss = MEGA_DF.filter(regex='gain_loss').fillna(0)  # getting just the market value of each ticker
gain_loss_df = portf_gain_loss.sum(axis=1)

print(gain_loss_df.head(10).to_string())
# plt.figure()
# gain_loss_df.plot()
# plt.grid()
# plt.show()
# exit()
portf_allvalues['portf_gain_loss'] = portf_gain_loss.sum(axis=1)  # summing all market values
# print('port value')
# print(portf_allvalues['portf_value'].to_string())

# exit()

# For the S&P500 price return
sp500 = pdr.get_data_yahoo('^GSPC', start_stocks, end_sp)
clean_header(sp500)

# Read and print the stock tickers that make up S&P500
# sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
# print(sp500.head().to_string())
# exit()

# getting the pct change
portf_allvalues = portf_allvalues.join(sp500['adj_close'], how='inner')
portf_allvalues.rename(columns={'adj_close': 'sp500_mktvalue'}, inplace=True)
portf_allvalues['ptf_value_pctch'] = (portf_allvalues['portf_value'].pct_change() * 100).round(2)
portf_allvalues['sp500_pctch'] = (portf_allvalues['sp500_mktvalue'].pct_change() * 100).round(2)
portf_allvalues['ptf_value_diff'] = (portf_allvalues['portf_value'].diff()).round(2)
portf_allvalues['sp500_diff'] = (portf_allvalues['sp500_mktvalue'].diff()).round(2)

# print(portf_allvalues.head().to_string())

# KPI's for portfolio
kpi_portfolio7d_abs = portf_allvalues.tail(7).ptf_value_diff.sum().round(2)
kpi_portfolio15d_abs = portf_allvalues.tail(15).ptf_value_diff.sum().round(2)
kpi_portfolio30d_abs = portf_allvalues.tail(30).ptf_value_diff.sum().round(2)
kpi_portfolio200d_abs = portf_allvalues.tail(200).ptf_value_diff.sum().round(2)
kpi_portfolio7d_pct = (kpi_portfolio7d_abs / portf_allvalues.tail(7).portf_value[0]).round(3) * 100
kpi_portfolio15d_pct = (kpi_portfolio15d_abs / portf_allvalues.tail(15).portf_value[0]).round(3) * 100
kpi_portfolio30d_pct = (kpi_portfolio30d_abs / portf_allvalues.tail(30).portf_value[0]).round(3) * 100
kpi_portfolio200d_pct = (kpi_portfolio200d_abs / portf_allvalues.tail(200).portf_value[0]).round(3) * 100

# KPI's for S&P500
kpi_sp500_7d_abs = portf_allvalues.tail(7).sp500_diff.sum().round(2)
kpi_sp500_15d_abs = portf_allvalues.tail(15).sp500_diff.sum().round(2)
kpi_sp500_30d_abs = portf_allvalues.tail(30).sp500_diff.sum().round(2)
kpi_sp500_200d_abs = portf_allvalues.tail(200).sp500_diff.sum().round(2)
kpi_sp500_7d_pct = (kpi_sp500_7d_abs / portf_allvalues.tail(7).sp500_mktvalue[0]).round(3) * 100
kpi_sp500_15d_pct = (kpi_sp500_15d_abs / portf_allvalues.tail(15).sp500_mktvalue[0]).round(3) * 100
kpi_sp500_30d_pct = (kpi_sp500_30d_abs / portf_allvalues.tail(30).sp500_mktvalue[0]).round(3) * 100
kpi_sp500_200d_pct = (kpi_sp500_200d_abs / portf_allvalues.tail(200).sp500_mktvalue[0]).round(3) * 100

initial_date = '2020-07-30'  # do not use anything earlier than your first trade
plotlydf_portfval = portf_allvalues[portf_allvalues.index > initial_date]
plotlydf_portfval = plotlydf_portfval[['portf_value', 'portf_gain_loss', 'sp500_mktvalue', 'ptf_value_pctch',
                                       'sp500_pctch', 'ptf_value_diff', 'sp500_diff']].reset_index().round(2)
# calculating cumulative growth since initial date
plotlydf_portfval['ptf_growth'] = plotlydf_portfval.portf_value / plotlydf_portfval['portf_value'].iloc[0]
plotlydf_portfval['sp500_growth'] = plotlydf_portfval.sp500_mktvalue / plotlydf_portfval['sp500_mktvalue'].iloc[0]
plotlydf_portfval.rename(columns={'index': 'date'}, inplace=True)  # needed for later
print(plotlydf_portfval.head().to_string())
print(plotlydf_portfval['portf_value'].head().to_string())

# plotting
CHART_THEME = 'plotly_white'  # others include seaborn, ggplot2, plotly_dark

chart_ptfvalue = go.Figure()  # generating a figure that will be updated in the following lines
chart_ptfvalue.add_trace(go.Scatter(x=plotlydf_portfval.date, y=plotlydf_portfval.portf_value,
                                    mode='markers',  # you can also use "lines+markers", or just "markers"
                                    name='Global Value'))
chart_ptfvalue.layout.template = CHART_THEME
chart_ptfvalue.layout.height = 1000
chart_ptfvalue.update_layout(margin=dict(t=50, b=50, l=25, r=25))  # this will help you optimize the chart space
chart_ptfvalue.update_layout(
    #     title='Global Portfolio Value (USD $)',
    xaxis_tickfont_size=12,
    yaxis=dict(
        title='Value: INR',
        titlefont_size=14,
        tickfont_size=12,
    ))
# chart_ptfvalue.update_xaxes(rangeslider_visible=False)
# chart_ptfvalue.update_layout(showlegend=False)
chart_ptfvalue.show()
# Gain / Loss
CHART_THEME = 'plotly_white'  # others include seaborn, ggplot2, plotly_dark

chart_ptfvalue = go.Figure()  # generating a figure that will be updated in the following lines
chart_ptfvalue.add_trace(go.Scatter(x=plotlydf_portfval.date, y=plotlydf_portfval.portf_gain_loss,
                                    mode='lines+markers',  # you can also use "lines+markers", or just "markers"
                                    name='Global Value'))
chart_ptfvalue.layout.template = CHART_THEME
chart_ptfvalue.layout.height = 1000
chart_ptfvalue.update_layout(margin=dict(t=50, b=50, l=25, r=25))  # this will help you optimize the chart space
chart_ptfvalue.update_layout(
    #     title='Global Portfolio Value (USD $)',
    xaxis_tickfont_size=12,
    yaxis=dict(
        title='Value: INR',
        titlefont_size=14,
        tickfont_size=12,
    ))
# chart_ptfvalue.update_xaxes(rangeslider_visible=False)
# chart_ptfvalue.update_layout(showlegend=False)
chart_ptfvalue.show()

print(list(pio.templates))

print(plotlydf_portfval)

fig2 = go.Figure(data=[
    go.Bar(name='Portfolio', x=plotlydf_portfval['date'], y=plotlydf_portfval['ptf_value_pctch']),
    go.Bar(name='SP500', x=plotlydf_portfval['date'], y=plotlydf_portfval['sp500_pctch'])
])
# Change the bar mode
fig2.update_layout(barmode='group')
fig2.layout.template = CHART_THEME
fig2.layout.height = 300
fig2.update_layout(margin=dict(t=50, b=50, l=25, r=25))
fig2.update_layout(
    #     title='% variation - Portfolio vs SP500',
    xaxis_tickfont_size=12,
    yaxis=dict(
        title='% change',
        titlefont_size=14,
        tickfont_size=12,
    ))
fig2.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="right",
    x=0.99))

fig2.show()

df = plotlydf_portfval[['date', 'ptf_growth', 'sp500_growth']].copy().round(3)
df['month'] = df.date.dt.month_name()  # date column should be formatted as datetime
df['weekday'] = df.date.dt.day_name()  # could be interesting to analyze weekday returns later
df['year'] = df.date.dt.year
# df['weeknumber'] = df.date.dt.week  # could be interesting to try instead of timeperiod
df['weeknumber'] = df.date.dt.isocalendar().week  # could be interesting to try instead of timeperiod
df['timeperiod'] = df.year.astype(str) + ' - ' + df.date.dt.month.astype(str).str.zfill(2)
df.head(5)

# getting the percentage change for each period. the first period will be NaN
sp = df.reset_index().groupby('timeperiod').last()['sp500_growth'].pct_change() * 100
ptf = df.reset_index().groupby('timeperiod').last()['ptf_growth'].pct_change() * 100
plotlydf_growth_compare = pd.merge(ptf, sp, on='timeperiod').reset_index().round(3)
plotlydf_growth_compare.head()

fig_growth2 = go.Figure()
fig_growth2.layout.template = CHART_THEME
fig_growth2.add_trace(go.Bar(
    x=plotlydf_growth_compare.timeperiod,
    y=plotlydf_growth_compare.ptf_growth.round(2),
    name='Portfolio'
))
fig_growth2.add_trace(go.Bar(
    x=plotlydf_growth_compare.timeperiod,
    y=plotlydf_growth_compare.sp500_growth.round(2),
    name='S&P 500',
))
fig_growth2.update_layout(barmode='group')
fig_growth2.layout.height = 600
fig_growth2.update_layout(margin=dict(t=50, b=50, l=25, r=25))
fig_growth2.update_layout(
    xaxis_tickfont_size=12,
    yaxis=dict(
        title='% change',
        titlefont_size=13,
        tickfont_size=12,
    ))

fig_growth2.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="right",
    x=0.99))
fig_growth2.show()

exit()

indicators_ptf = go.Figure()
indicators_ptf.layout.template = CHART_THEME
indicators_ptf.add_trace(go.Indicator(
    mode="number+delta",
    value=kpi_portfolio7d_pct,
    number={'suffix': " %"},
    title={"text": "<br><span style='font-size:0.7em;color:gray'>7 Days</span>"},
    delta={'position': "bottom", 'reference': kpi_sp500_7d_pct, 'relative': False},
    domain={'row': 0, 'column': 0}))

indicators_ptf.add_trace(go.Indicator(
    mode="number+delta",
    value=kpi_portfolio15d_pct,
    number={'suffix': " %"},
    title={"text": "<span style='font-size:0.7em;color:gray'>15 Days</span>"},
    delta={'position': "bottom", 'reference': kpi_sp500_15d_pct, 'relative': False},
    domain={'row': 1, 'column': 0}))

indicators_ptf.add_trace(go.Indicator(
    mode="number+delta",
    value=kpi_portfolio30d_pct,
    number={'suffix': " %"},
    title={"text": "<span style='font-size:0.7em;color:gray'>30 Days</span>"},
    delta={'position': "bottom", 'reference': kpi_sp500_30d_pct, 'relative': False},
    domain={'row': 2, 'column': 0}))

indicators_ptf.add_trace(go.Indicator(
    mode="number+delta",
    value=kpi_portfolio200d_pct,
    number={'suffix': " %"},
    title={"text": "<span style='font-size:0.7em;color:gray'>200 Days</span>"},
    delta={'position': "bottom", 'reference': kpi_sp500_200d_pct, 'relative': False},
    domain={'row': 3, 'column': 1}))

indicators_ptf.update_layout(
    grid={'rows': 4, 'columns': 1, 'pattern': "independent"},
    margin=dict(l=50, r=50, t=30, b=30)
)

indicators_ptf.show()

indicators_sp500 = go.Figure()
indicators_sp500.layout.template = CHART_THEME
indicators_sp500.add_trace(go.Indicator(
    mode="number+delta",
    value=kpi_sp500_7d_pct,
    number={'suffix': " %"},
    title={"text": "<br><span style='font-size:0.7em;color:gray'>7 Days</span>"},
    domain={'row': 0, 'column': 0}))

indicators_sp500.add_trace(go.Indicator(
    mode="number+delta",
    value=kpi_sp500_15d_pct,
    number={'suffix': " %"},
    title={"text": "<span style='font-size:0.7em;color:gray'>15 Days</span>"},
    domain={'row': 1, 'column': 0}))

indicators_sp500.add_trace(go.Indicator(
    mode="number+delta",
    value=kpi_sp500_30d_pct,
    number={'suffix': " %"},
    title={"text": "<span style='font-size:0.7em;color:gray'>30 Days</span>"},
    domain={'row': 2, 'column': 0}))

indicators_sp500.add_trace(go.Indicator(
    mode="number+delta",
    value=kpi_sp500_200d_pct,
    number={'suffix': " %"},
    title={"text": "<span style='font-size:0.7em;color:gray'>200 Days</span>"},
    domain={'row': 3, 'column': 1}))

indicators_sp500.update_layout(
    grid={'rows': 4, 'columns': 1, 'pattern': "independent"},
    margin=dict(l=50, r=50, t=30, b=30)
)
# indicators_sp500.show()
exit()
# Getting the prices for the TOP Stocks
last_positions = final_filtered.groupby(['ticker']).agg({'cml_units': 'last', 'cml_cost': 'last',
                                                         'gain_loss': 'sum', 'cashflow': 'sum'}).reset_index()

curr_prices = []
for tick in last_positions['ticker']:
    stonk = yf.Ticker(tick)
    price = stonk.info['regularMarketPrice']
    curr_prices.append(price)
    print(f'Done for {tick}')

print(len(curr_prices))

last_positions['price'] = curr_prices
last_positions['current_value'] = (last_positions.price * last_positions.cml_units).round(2)
last_positions['avg_price'] = (last_positions.cml_cost / last_positions.cml_units).round(2)
last_positions = last_positions.sort_values(by='current_value', ascending=False)

print(last_positions.to_string())

donut_top = go.Figure()
donut_top.layout.template = CHART_THEME
donut_top.add_trace(go.Pie(labels=last_positions.head(15).ticker, values=last_positions.head(15).current_value))
donut_top.update_traces(hole=.7, hoverinfo="label+value+percent")
donut_top.update_traces(textposition='outside', textinfo='label+value')
donut_top.update_layout(showlegend=False)
donut_top.update_layout(margin=dict(t=50, b=50, l=25, r=25))
donut_top.show()

app = dash.Dash()

app.layout = dbc.Container(
    [
        dbc.Row(dbc.Col(html.H2('PORTFOLIO OVERVIEW', className='text-center text-primary, mb-3'))),  # header row

        dbc.Row([  # start of second row
            dbc.Col([  # first column on second row
                html.H5('Total Portfolio Value ($USD)', className='text-center'),
                dcc.Graph(id='chrt-portfolio-main',
                          figure=chart_ptfvalue,
                          style={'height': 550}),
                html.Hr(),
            ], width={'size': 8, 'offset': 0, 'order': 1}),  # width first column on second row
            dbc.Col([  # second column on second row
                html.H5('Portfolio', className='text-center'),
                dcc.Graph(id='indicators-ptf',
                          figure=indicators_ptf,
                          style={'height': 550}),
                html.Hr()
            ], width={'size': 2, 'offset': 0, 'order': 2}),  # width second column on second row
            dbc.Col([  # third column on second row
                html.H5('S&P500', className='text-center'),
                dcc.Graph(id='indicators-sp',
                          figure=indicators_sp500,
                          style={'height': 550}),
                html.Hr()
            ], width={'size': 2, 'offset': 0, 'order': 3}),  # width third column on second row
        ]),  # end of second row

        dbc.Row([  # start of third row
            dbc.Col([  # first column on third row
                html.H5('Monthly Return (%)', className='text-center'),
                dcc.Graph(id='chrt-portfolio-secondary',
                          figure=fig_growth2,
                          style={'height': 380}),
            ], width={'size': 8, 'offset': 0, 'order': 1}),  # width first column on second row
            dbc.Col([  # second column on third row
                html.H5('Top 15 Holdings', className='text-center'),
                dcc.Graph(id='pie-top15',
                          figure=donut_top,
                          style={'height': 380}),
            ], width={'size': 4, 'offset': 0, 'order': 2}),  # width second column on second row
        ])  # end of third row

    ], fluid=True)

if __name__ == "__main__":
    app.run_server(debug=True, port=8058)

app._terminate_server_for_port("localhost", 8058)

SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '12rem',
    'padding': '2rem 1rem',
    'background-color': 'lightgray',
}
CONTENT_STYLE = {
    'margin-left': '15rem',
    'margin-right': '2rem',
    'padding': '2rem' '1rem',
}

child = dbc.Container(
    [
        dbc.Row(dbc.Col(html.H2('PORTFOLIO OVERVIEW', className='text-center text-primary, mb-3'))),
        dbc.Row([
            dbc.Col([
                html.H5('Total Portfolio Value ($USD)', className='text-center'),
                dcc.Graph(id='chrt-portfolio-main',
                          figure=chart_ptfvalue,
                          style={'height': 550}),
                html.Hr(),

            ],
                width={'size': 8, 'offset': 0, 'order': 1}),
            dbc.Col([
                html.H5('Portfolio', className='text-center'),
                dcc.Graph(id='indicators-ptf',
                          figure=indicators_ptf,
                          style={'height': 550}),
                html.Hr()
            ],
                width={'size': 2, 'offset': 0, 'order': 2}),
            dbc.Col([
                html.H5('S&P500', className='text-center'),
                dcc.Graph(id='indicators-sp',
                          figure=indicators_sp500,
                          style={'height': 550}),
                html.Hr()
            ],
                width={'size': 2, 'offset': 0, 'order': 3}),
        ]),  # end of second row
        dbc.Row([
            dbc.Col([
                html.H5('Monthly Return (%)', className='text-center'),
                dcc.Graph(id='chrt-portfolio-secondary',
                          figure=fig_growth2,
                          style={'height': 380}),
            ],
                width={'size': 8, 'offset': 0, 'order': 1}),
            dbc.Col([
                html.H5('Top 15 Holdings', className='text-center'),
                dcc.Graph(id='pie-top15',
                          figure=donut_top,
                          style={'height': 380}),
            ],
                width={'size': 4, 'offset': 0, 'order': 2}),
        ])

    ], fluid=True)

sidebar = html.Div(
    [
        #         html.H5("Navigation Menu", className='display-6'),
        html.Hr(),
        html.P('Navigation Menu', className='text-center'),

        dbc.Nav(
            [
                dbc.NavLink('Home', href="/", active='exact'),
                dbc.NavLink('Page2', href="/page-2", active='exact')
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id='page-content', children=child, style=CONTENT_STYLE)

# app = JupyterDash(__name__, external_stylesheets=[dbc.themes.SPACELAB])
app = dash.Dash()
# app = JupyterDash(__name__)
app.layout = html.Div([
    dcc.Location(id='url'),
    sidebar,
    content
])

if __name__ == "__main__":
    app.run_server(debug=True, port=8056)
