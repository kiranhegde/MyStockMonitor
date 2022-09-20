import os
import pandas as pd

from PyQt5 import QtWebEngineWidgets
from PyQt5.QtCore import Qt, QPoint, pyqtSlot, QDateTime
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QWidget, QMenu, QAction, QTableView, QMessageBox, \
    QVBoxLayout, QHBoxLayout, QGroupBox, \
    QAbstractItemView, \
    QHeaderView, QSplitter, QFileDialog

# from babel.numbers import format_currency
import datetime
import yfinance as yf

from mysql_tools.mysql_crud import mysql_table_crud
from mysql_tools.tables_and_headers import CURRENT_HOLDING_DB_TO_DISPLAY, CURRENT_HOLDINGS_HEADER_DROP_LIST, CURRENT_HOLDINGS_HEADER_DISPLAY_LIST, \
    TOTAL_HOLDINGS_DB_HEADER, CURRENT_HOLDINGS_HEADER_DISPLAY_LIST2DB,\
    INDEX_DB_TABLE_NAME,INDEXES_DB_HEADER,INDEX_NAME_DICT,INDEX_HEADER_DISPLAY_LIST,INDEX_LIST_DISPLAY


from gui_widgets.gui_widgets_for_adding_new_stock import add_new_stock as new_stock
from gui_widgets.gui_widgets_for_editing_selected_stock import edit_selected_stock
from gui_widgets.gui_widgets_for_selling_selected_stock import sell_selected_stock
from gui_widgets.gui_widgets_average_stocks import average_stocks

import copy
# from DataBase.mysql_crud import mysql_table_crud
from utility.tableViewModel import pandasModel
from utility.fonts_style import TABLE_HEADER_FONT, TABLE_FONT
from utility.utility_functions import make_nested_dict, parse_str
from os.path import expanduser
from utility.date_time import DATE_TIME, DATE_FMT_YMD, DATE_FMT_DMY
from utility.utility_functions import reduce_mem_usage, gen_id, \
    symbol_date_string, symbol_date_split,\
    create_current_index_csv_file_names

from plotly import graph_objs as go
from plotly.subplots import make_subplots
# from plotly.tools import make_subplots
from ta.trend import MACD
from ta.momentum import StochasticOscillator

global DEFAULT_PATH
usr_path = expanduser("~")
DEFAULT_PATH = f"{usr_path}/Desktop/"


class indexes_display(QWidget):
    def __init__(self, **mysql_data):
        super().__init__()
        # self.setWindowTitle("Balance test")
        self.db_cfg = mysql_data
        self.UI()

    def UI(self):
        self.connect_to_tables()

        # new_stock_addition={}
        # ref_no = gen_id(**self.db_cfg)
        # new_stock_addition['id'] = 0
        # new_stock_addition['ref_number'] = ref_no
        # tdate="01-01-2015"
        # new_stock_addition['from_date'] = pd.to_datetime(tdate, format=DATE_FMT_DMY)
        # # new_stock_addition['type'] = TRADE_TYPE[0]
        #
        # new_stock_addition['indice_name'] = "INDIAVIX"
        # new_stock_addition['remarks'] = "INDIAVIX"
        # listt = list(new_stock_addition.values())
        # vals_tuple = [tuple(listt)]
        # messge = self.total_index_details.insert_row_by_column_values(row_val=vals_tuple)
        # print(messge)
        # exit()

        # "NIFTYPHARMA": "^CNXPHARMA",
        # "NIFTYMETAL": "^CNXMETAL",
        # "NIFTYFMCG": "^CNXFMCG",
        # "NIFTYENERGY": "^CNXENERGY",
        # "NIFTYAUTO": "^CNXAUTO",
        # "NIFTYFMCG": "^CNXFMCG"
        symbol_df = self.get_indexes_details()
        # self.index_trend_data_df = self.get_indexes_details()
        # print(INDEX_LIST_DISPLAY)
        self.index_trend_data_df = symbol_df.loc[:, INDEX_LIST_DISPLAY]

        # print(self.index_trend_data_df.to_string())
        file_names=self.create_index_filename(self.index_trend_data_df)
        # print(file_names)

        # self.current_index_history = self.extract_current_holdings_history()
        self.current_index_history = self.extract_current_index_history(file_names)
        # print(self.current_index_history.keys())

        # exit()
        self.widgets()
        self.layouts()

    def widgets(self):
        self.data_plot_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.index_trend_data_df.columns = INDEX_HEADER_DISPLAY_LIST
        self.holdingModel, self.holdingTable = self.tableViewDataModel(self.index_trend_data_df)
        self.holdingModel.sort(1, Qt.DescendingOrder)
        self.holdingTable.installEventFilter(self)
        self.holdingTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.holdingTable.setColumnHidden(0, True)
        self.holdingTable.customContextMenuRequested.connect(self.rightClickMenuPayIn)

    def connect_to_tables(self):
        self.total_index_details = mysql_table_crud(db_table=INDEX_DB_TABLE_NAME,
                                                    db_header=INDEXES_DB_HEADER,
                                                    **self.db_cfg)

    def get_indexes_details(self):
        data = make_nested_dict()
        for col in INDEXES_DB_HEADER:
            data[col] = None
        data = self.total_index_details.read_row_by_column_values()
        df = pd.DataFrame(data)
        # mask = df["current_holding"] == True
        # symbol_df = df.loc[mask].copy()

        # required_columns=['ref_number','equity', 'date', 'avg_price', 'quantity']
        # ['Reference', 'Equity', 'Buy Date', 'Avg. Price', 'Quantity']
        # CURRENT_HOLDING_LIST_DISPLAY
        # symbol_df = symbol_df.loc[:, CURRENT_HOLDING_LIST_DISPLAY]
        # symbol_df.columns = CURRENT_HOLDINGS_HEADER_DISPLAY_LIST

        return df

    # def create_current_index_csv_file_names(self,symbol_df):
    #     # mask = df["current_holding"] == True
    #     # symbol_df = df[mask]
    #     # print(symbol_df.head(3).to_string())
    #     # exit()
    #     symbol_csv_path_list = make_nested_dict()
    #     for index, row in symbol_df.iterrows():
    #         symbol = row['indice_name']
    #         buy_date = row['from_date']
    #         symbol_buy_date = symbol_date_string(symbol, buy_date)
    #         path_to_csv_file = os.path.join(PATH_TO_DATABASE_CURRENT_INDEX, f"{symbol_buy_date}_history.csv")
    #         symbol_csv_path_list[symbol_buy_date] = path_to_csv_file
    #     return symbol_csv_path_list

    def create_index_filename(self,index_trend_data_df):
        # return get_current_holdings_history(self.current_holding_data_df)
        current_holdings_csv_file_names = create_current_index_csv_file_names(index_trend_data_df)
        return current_holdings_csv_file_names
        # return get_current_holdings_history_mp(current_holdings_csv_file_names)

    def extract_current_index_history(self,holdings_csv_file_names):
        # https://stackoverflow.com/questions/62130801/parallel-processing-in-python-to-fill-a-dictionary-with-the-value-as-a-dictionar
        # from multiprocessing import Process, Manager
        current_holding_history = make_nested_dict()

        # current_holdings_csv_file_names = create_current_holdings_csv_file_names(current_holding_data_df)

        def csv_file_read(filename):
            f = pd.read_csv(filename)
            return f

        def download_and_read_csv(symbol, filename):
            # data = yf.download(symbol_ns, threads=True)
            # print(symbol)
            # print(filename)
            data = yf.download(symbol,threads=True)
            data.to_csv(filename)
            f = csv_file_read(filename)
            return f

        def compile_stock_data(result):
            df = pd.DataFrame(result)
            mask = df['Date'] > str(deltatime)
            for i in ['Open', 'Close', 'High', 'Low', 'Adj Close', 'Volume']:
                df[i] = df[i].astype('float64')
            df = df.loc[mask].copy()
            current_holding_history[symbol_buy_date] = reduce_mem_usage(df)

        # pool = Pool(processes=6)
        jobs = []
        deltatime = datetime.date.today() - datetime.timedelta(5 * 365)
        for symbol_buy_date, path_to_csv_file in holdings_csv_file_names.items():

            if os.path.isfile(path_to_csv_file):
                csv_data = csv_file_read(path_to_csv_file)
                compile_stock_data(csv_data)
                # process=multiprocessing.Process(target=compile_stock_data,args=(csv_data))
                # jobs.append(process)
                # pool.apply_async(csv_file_read, args=(path_to_csv_file,), callback=compile_stock_data)
            else:
                print(path_to_csv_file, 'path missing')
                symbol, buy_date = symbol_date_split(symbol_buy_date)
                symbol_ns = f"{INDEX_NAME_DICT[symbol]}"
                csv_data = download_and_read_csv(symbol_ns, path_to_csv_file)
                compile_stock_data(csv_data)
                # process = multiprocessing.Process(target=compile_stock_data, args=(csv_data))
                # jobs.append(process)

                # pool.apply_async(download_and_read_csv, args=(symbol_ns,path_to_csv_file,), callback=compile_stock_data)

        # # Start the processes (i.e. calculate the random number lists)
        # for j in jobs:
        #     j.start()
        #
        # # Ensure all of the processes have finished
        # for j in jobs:
        #     j.join()

        # pool.close()
        # pool.join()
        return current_holding_history

    def layouts(self):
        self.mainLayout = QHBoxLayout()
        self.horizontalSplitter = QSplitter(Qt.Horizontal)
        self.leftVsplitter = QSplitter(Qt.Vertical)
        self.rightVsplitter = QSplitter(Qt.Vertical)
        self.rightBottomLayout = QHBoxLayout()

        self.leftLayout = QVBoxLayout()
        self.rightLayout = QVBoxLayout()
        self.leftTopGroupBox = QGroupBox("Index Names")
        self.rightTopGroupBox = QGroupBox("Script Information")

        # self.rightBottomWidget = QWidget()
        # self.rightBottomWidget.setLayout(self.rightBottomLayout)
        self.leftLayout.addWidget(self.holdingTable)
        ncol = self.holdingModel.columnCount()
        row_data = []
        for col in range(ncol):
            val = self.holdingTable.model().index(0, col).data()
            row_data.append(val)

        # print(row_data)
        # self.plot_graphs()
        self.plot_graphs(buy_date=row_data[0], symbol=row_data[1])
        self.rightLayout.addWidget(self.data_plot_browser)

        fnt_GBox = QFont()
        fnt_GBox.setPointSize(10)
        fnt_GBox.setBold(True)
        fnt_GBox.setFamily("Arial")
        self.leftTopGroupBox.setLayout(self.leftLayout)
        self.rightTopGroupBox.setLayout(self.rightLayout)
        self.leftTopGroupBox.setFont(fnt_GBox)
        self.leftTopGroupBox.setStyleSheet('QGroupBox:title {color: blue;}')
        self.rightTopGroupBox.setFont(fnt_GBox)
        self.rightTopGroupBox.setStyleSheet('QGroupBox:title {color: green;}')

        self.leftVsplitter.addWidget(self.leftTopGroupBox)
        self.rightVsplitter.addWidget(self.rightTopGroupBox)
        # self.rightVsplitter.addWidget(self.rightBottomWidget)
        # self.rightVsplitter.setStretchFactor(0, 97)
        # self.rightVsplitter.setStretchFactor(1, 3)

        self.horizontalSplitter.addWidget(self.leftVsplitter)
        self.horizontalSplitter.addWidget(self.rightVsplitter)
        self.horizontalSplitter.setStretchFactor(0, 5)
        self.horizontalSplitter.setStretchFactor(1, 95)
        self.horizontalSplitter.setContentsMargins(0, 0, 0, 0)
        self.horizontalSplitter.handle(0)

        self.mainLayout.addWidget(self.horizontalSplitter)
        self.setLayout(self.mainLayout)

    # def plot_graphs(self, price=100, buy_date=datetime.date.today(), symbol="DMART"):
    def plot_graphs(self, moving_avg = 'SMA',buy_date=datetime.date.today(),
                    symbol="NIFTY50"):
        # https: // stackoverflow.com / questions / 47797383 / plotly - legend - next - to - each - subplot - python
        # buy_date = pd.to_datetime(buy_date).date()
        # print(type(buy_date),buy_date)
        buy_date = datetime.datetime.strptime(buy_date, DATE_FMT_DMY)
        buy_date = datetime.datetime.strftime(buy_date, DATE_FMT_YMD)
        # buy_date = datetime.datetime.strptime(buy_date, DATE_FMT_YMD)
        symbol_buy_date = symbol_date_string(symbol, buy_date)
        # print(symbol_buy_date)
        df = self.current_index_history[symbol_buy_date]
        # exit()

        # print(symbol)
        # print(len(df))
        # print(type(df))
        # print(df.empty)
        if len(df) == 0:
            QMessageBox.information(self, f'{symbol} history missing !!',
                                    f'Please download stock history of {symbol} ')

            return

        # exit()
        if symbol_buy_date in self.current_index_history.keys() and not self.current_index_history[
            symbol_buy_date].empty:
            # if symbol in self.holding_history.keys() and len(df) != 0 and :
            df = self.current_index_history[symbol_buy_date]
            fig = make_subplots(rows=4, cols=1,
                                # column_widths=[0.6, 0.4],
                                row_heights=[0.7, 0.1, 0.1, 0.1],
                                vertical_spacing=0.01,
                                shared_xaxes=True)
            # removing rangeslider
            # fig.update_layout(xaxis_rangeslider_visible=False)

            # Plot OHLC on 1st subplot (using the codes from before)
            fig.add_trace(go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'],
                                         name='Market Value',
                                         showlegend=True))

            # fig.show()
            # MACD
            macd = MACD(close=df['Close'],
                        window_slow=26,
                        window_fast=12,
                        window_sign=9)
            # stochastics
            stoch = StochasticOscillator(high=df['High'],
                                         close=df['Close'],
                                         low=df['Low'],
                                         window=14,
                                         smooth_window=3)

            # removing all empty dates
            # build complete timeline from start date to end date
            dt_all = pd.date_range(start=df.index[0], end=df.index[-1])
            # retrieve the dates that ARE in the original datset
            dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(df.index)]
            # print(dt_obs)
            # define dates with missing values
            dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in dt_obs]
            # fig.update_layout(xaxis_rangebreaks=[dict(values=dt_breaks)])

            fig.update_layout(margin=go.layout.Margin(
                l=80,  # left margin
                r=0,  # right margin
                b=30,  # bottom margin
                t=80  # top margin
            ))
            # fig.show()

            # add moving averages to df
            if moving_avg == 'SMA':
                sma_dict={'SMA20':[20,'black'],'SMA44':[44,'coral'],
                          'SMA50':[50,'blue'],'SMA100':[100,'green'],
                          'SMA200':[200,'red']}

                for sma,val in sma_dict.items():
                    df[sma] = df['Close'].rolling(window=val[0],
                                                     min_periods=1).mean()
                    fig.add_trace(go.Scatter(x=df['Date'],
                                             y=df[sma],
                                             opacity=0.7,
                                             line=dict(color=val[1], width=2),
                                             name=sma))
            elif moving_avg == 'EMA':
                # 10 -short term (traders)
                # 21 -short term(traders)
                # 63 -medium term(investors,marathon trades)
                # 200 -long term(pure long term)
                # https://towardsdatascience.com/making-a-trade-call-using-simple-moving-average-sma-crossover-strategy-python-implementation-29963326da7a
                ema_dict = {'EMA10': [10, 'black'], 'EMA12': [12, 'coral'],
                            'EMA21': [21, 'blue'], 'EMA26': [26, 'green'],
                            'EMA55': [55, 'red'], 'EMA63': [63, 'darkviolet'],
                            'EMA200': [200, 'olive']}
                for ema, val in ema_dict.items():
                    df[ema] = df['Close'].ewm(span=val[0],
                                              adjust=False, ).mean()
                    fig.add_trace(go.Scatter(x=df['Date'],
                                             y=df[ema],
                                             opacity=0.7,
                                             line=dict(color=val[1], width=2),
                                             name=ema))


            # fig.add_hline(y=price, line_width=2, line_color="red", opacity=0.7, name='Buy Avg.')

            # Plot volume trace on 2nd row
            colors = ['green' if row['Open'] - row['Close'] >= 0
                      else 'red' for index, row in df.iterrows()]
            fig.add_trace(go.Bar(x=df['Date'],
                                 y=df['Volume'],
                                 marker_color=colors,
                                 showlegend=False
                                 ), row=2, col=1)

            # Plot MACD trace on 3rd row
            colors = ['green' if val >= 0
                      else 'red' for val in macd.macd_diff()]
            fig.add_trace(go.Bar(x=df['Date'],
                                 y=macd.macd_diff(),
                                 marker_color=colors,
                                 showlegend=False,
                                 ), row=3, col=1)
            fig.add_trace(go.Scatter(x=df['Date'],
                                     y=macd.macd(),
                                     showlegend=False,
                                     line=dict(color='red', width=1)
                                     ), row=3, col=1)
            fig.add_trace(go.Scatter(x=df['Date'],
                                     y=macd.macd_signal(),
                                     showlegend=False,
                                     line=dict(color='blue', width=1)
                                     ), row=3, col=1)

            # Plot stochastics trace on 4th row
            fig.add_trace(go.Scatter(x=df['Date'],
                                     y=stoch.stoch(),
                                     showlegend=False,
                                     line=dict(color='red', width=1)
                                     ), row=4, col=1)
            fig.add_trace(go.Scatter(x=df['Date'],
                                     y=stoch.stoch_signal(),
                                     showlegend=False,
                                     line=dict(color='blue', width=1)
                                     ), row=4, col=1)

            start_date = df['Date'].iloc[0]
            end_date = datetime.date.today() + datetime.timedelta(30)
            # update layout by changing the plot size, hiding legends & rangeslider, and removing gaps between dates
            # fig.update_layout(height=900, width=1200,
            fig.update_layout(showlegend=True,
                              xaxis_rangeslider_visible=False,
                              xaxis_rangebreaks=[dict(values=dt_breaks)])

            # update y-axis label
            fig.update_yaxes(title_text="Price[INR]", row=1, col=1)
            fig.update_yaxes(title_text="Volume", row=2, col=1)
            fig.update_yaxes(title_text="MACD", showgrid=True, row=3, col=1)
            fig.update_yaxes(title_text="RSI", row=4, col=1)

            # hide dates with no values
            fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])
            fig.update_xaxes(minor_showgrid=True)
            fig.update_layout(xaxis=dict(range=[start_date, end_date]))
            # remove rangeslider
            # fig.update_layout(xaxis_rangeslider_visible=False)
            # # add chart title
            fig.update_layout(title=symbol)

            fig.update_layout(legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ))
            # fig.update_traces(quartilemethod="linear")  # or "inclusive", or "linear" by default
            self.data_plot_browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        else:
            QMessageBox.information(self, f'{symbol} history missing !!',
                                    f'Please download stock history of {symbol} ')

    def plot_graphs0(self, price=100, symbol="DMART"):

        if symbol in self.holding_history.keys():
            df = self.holding_history[symbol]
            # finding the moving average of 20 periods
            avg_20 = df.Close.rolling(window=20, min_periods=1).mean()

            # finding the moving average of 50 periods
            avg_50 = df.Close.rolling(window=50, min_periods=1).mean()

            # finding the moving average of 50 periods
            avg_100 = df.Close.rolling(window=100, min_periods=1).mean()

            # finding the moving average of 200 periods
            avg_200 = df.Close.rolling(window=200, min_periods=1).mean()

            set1 = {
                'x': df.Date,
                'open': df.Open,
                'close': df.Close,
                'high': df.High,
                'low': df.Low,
                'type': 'candlestick',
            }

            set2 = {
                'x': df.Date,
                'y': avg_20,
                'type': 'scatter',
                'mode': 'lines',
                'line': {
                    'width': 2,
                    'color': 'blue'
                },
                # 'name': 'Moving Average of 20 periods'
                'name': '20 SMA'
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
                # 'name': 'Moving Average of 50 periods'
                'name': '50 SMA'
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
                # 'name': 'Moving Average of 100 periods'
                'name': '100 SMA'
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
                # 'name': 'Moving Average of 200 periods'
                'name': '200 SMA'
            }

            data = [set1, set2, set3, set4, set5]
            # Config graph layout
            layout = go.Layout({
                'title': {
                    'text': symbol,
                    'font': {
                        'size': 18
                    }
                }
            })
            fig = go.Figure(data=data, layout=layout)
            # fig.add_hline(y=price, line_width=2, line_dash="dash", line_color="red")
            fig.add_hline(y=price, line_width=2, line_color="red")
            fig.update_xaxes(title_text='Day')
            fig.update_yaxes(title_text='Price[Rs.]')
            fig.update_layout(legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ))
            # fig.update_traces(quartilemethod="linear")  # or "inclusive", or "linear" by default
            self.data_plot_browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
            # self.data_plot_browser.setHtml(fig.to_html())
            # fig.show()

    def tableViewDataModel(self, data):

        Tview = QTableView()
        # fnt1 = QFont()
        # fnt1.setPointSize(10)
        # fnt1.setBold(True)
        # fnt1.setFamily("Arial")
        #
        # fnt2 = QFont()
        # fnt2.setPointSize(9)
        # # fnt2.setBold(True)
        # fnt2.setFamily("Arial")

        # https: // forum.qt.io / topic / 109144 / tableview -        not -updated - after - calling - datachanged / 11
        # self.model = pandasModel()
        # data.tableView.setModel(self.model)

        # size policy
        # Tview.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        # Tview.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)(display doesnot fit to screen)
        #
        Tview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        Tview.setSelectionBehavior(QAbstractItemView.SelectRows)
        # Tview.setWordWrap(True)

        Tview.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        Tview.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        Tview.setAlternatingRowColors(True)
        Tview.setSortingEnabled(True)
        Tview.setShowGrid(True)
        Tview.verticalHeader().setVisible(False)
        Tview.verticalHeader().hide()

        """
            Forbid resizing(speeds up)
        """
        header = Tview.horizontalHeader()
        header.setFont(TABLE_HEADER_FONT)
        header.setStyleSheet("color: blue;")
        Tview.setFont(TABLE_FONT)
        Tview.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        Tmodel = pandasModel(data)
        # Tmodel.setHorizontalHeaderLabels(header_list)
        Tview.setModel(Tmodel)

        return Tmodel, Tview

    def casesheet_list_menu(self, position):
        # print("agency menu")
        # Popup menu
        popMenu = QMenu()
        # newAct = QAction("New", self)
        # copyAct = QAction("Copy", self)
        # delAct = QAction("Delete", self)
        sort_all = QAction("Sort", self)
        renameAct = QAction("Rename", self)
        excelAct = QAction("Excel Report", self)
        clearAct = QAction("Unpaid Cleared", self)
        # Check if it is on the item when you right-click,
        # if it is not, copy, delete and rename will not be displayed.
        # 'New' item wil be displayed even if it is not clied on the item
        # popMenu.addAction(newAct)
        if self.Holding_List.itemAt(position):
            # popMenu.addAction(newAct)
            popMenu.addAction(sort_all)
            popMenu.addAction(renameAct)
            popMenu.addAction(excelAct)
            # popMenu.addAction(delAct)
            popMenu.addAction(clearAct)

        # newAct.triggered.connect(self.new_casesheet)
        # copyAct.triggered.connect(self.copy_group)
        sort_all.triggered.connect(self.sort_casesheet)
        renameAct.triggered.connect(self.rename_casesheet)
        excelAct.triggered.connect(self.export2excel_casesheet)
        # delAct.triggered.connect(self.delete_casesheet)
        clearAct.triggered.connect(self.clear_casesheet)
        popMenu.exec_(self.Holding_List.mapToGlobal(position))

    def sort_casesheet(self):
        # self.List_of_casesheet.sortItems()
        self.Holding_List.sortItems()

    def new_casesheet(self):
        pass

    def export2excel_casesheet(self):
        row = self.Holding_List.currentRow()
        item = self.Holding_List.item(row)
        item_name = item.text()
        pname = item_name.split('_')[0]
        mobileNo = item_name.split('_')[1]
        pname_mobile_old = f" patient_name = '{pname}'  and  mobile_no = '{mobileNo}' "
        mask1 = self.df_reception_payin["Patient Name"] == pname
        excel2report_df = self.df_reception_payin.loc[mask1]
        if not excel2report_df.isnull().values.all():
            excel2report_df['Date'] = excel2report_df['Date'].dt.strftime(DATE_FMT_DMY)
        classsum1 = excel2report_df.sum(axis=0)
        # sum_bill = classsum1["Cash"] + classsum1["CreditCard"] + classsum1["DebitCard"] + classsum1["EFT"] - \
        #            classsum1["CreditNote"]

        classsum1['Bill Number'] = "Total ->"
        classsum1['Date'] = ""
        classsum1['Patient Name'] = ""
        classsum1['Department'] = ""
        classsum1['Remarks'] = ""

        classsum2 = copy.deepcopy(classsum1)
        classsum2['Bill Number'] = "Grand Total ->"
        classsum2['Cash'] = ""
        classsum2['CreditCard'] = ""
        classsum2['DebitCard'] = ""
        classsum2['EFT'] = ""
        classsum2['Unpaid'] = ""
        classsum2['CreditNote'] = ""

        # print(classsum1.iloc["Total ->"].sum(axis=1))
        # grand_total = "{:.{}f}".format(sum_bill["credit_note"].sum(), 3)

        excel2report_df = excel2report_df.append(classsum1, ignore_index=True).fillna(" ")
        # print(excel2report_df.to_string())
        last_row = classsum1.to_dict()
        # print(last_row)

        grand_total = parse_str(last_row['Unpaid']) - (parse_str(last_row['Cash']) +
                                                       parse_str(last_row['CreditCard']) +
                                                       parse_str(last_row['DebitCard']) +
                                                       parse_str(last_row['EFT']) +
                                                       parse_str(last_row['CreditNote']))
        grand_total = "{:.{}f}".format(grand_total, 3)
        classsum2['Date'] = grand_total
        excel2report_df = excel2report_df.append(classsum2, ignore_index=True).fillna(" ")
        # print("#", grand_total)
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog

        fname = STATEMENT_EXCEL_PREFIX + "_" + str(item_name)

        # print(fname,self.userEntry.currentText())
        # print("$",os.pwd)

        fpath = f"{DEFAULT_PATH}{fname}"
        # print(fpath)

        file_path, ext = QFileDialog.getSaveFileName(self, "Save As", fpath, "(*.xlsx)",
                                                     options=options)
        # print(file_path, ext)
        if [file_path, ext] != [None, None]:
            if file_path != "":
                try:
                    writer_to_excel = pd.ExcelWriter(file_path)
                    with writer_to_excel as writer:
                        excel2report_df.to_excel(writer, sheet_name='BalanceSheet', index=False)
                        # excel2report_df.to_excel(writer, sheet_name='Pay_OUT', index=False)
                except Exception as e:
                    mbox0 = QMessageBox.warning(self, "Permission denied..",
                                                f"File may be open .. \n Please close the file and try. \n {e}",
                                                QMessageBox.Close)

    def rename_casesheet(self):

        # item=self.List_of_casesheet.currentItem()
        row = self.Holding_List.currentRow()
        item = self.Holding_List.item(row)
        item_name = item.text()
        if item_name == "Others":
            QMessageBox.information(self, 'Renaming Failed !!',
                                    f"'{item_name}' cannot be renamed !")
        else:
            pname = item_name.split('_')[0]
            mobileNo = item_name.split('_')[1]
            pname_mobile_old = f" patient_name = '{pname}'  and  mobile_no = '{mobileNo}' "
            mask1 = self.df_reception_payin["Patient Name"] == pname

            name_mobile_inp = get_name_mobile_no(pname, mobile_no=mobileNo)
            if name_mobile_inp.exec_() == name_mobile_inp.Accepted:
                pnameNew, mobile_number = name_mobile_inp.get_inp()
                if pnameNew.strip() == "":
                    pnameNew = pname
                if mobile_number.strip() == "":
                    pnameNew = mobileNo

            self.df_reception_payin.loc[mask1, ["Patient Name"]] = pnameNew
            self.holdingModel.update(self.df_reception_payin, key="New")
            self.holdingModel.layoutChanged.emit()
            self.holdingTable.clearSelection()
            pname_mobile = f" patient_name = '{pnameNew}',mobile_no = '{mobile_number}'"
            messge = self.total_index_details.update_rows_by_column_values(set_argument=pname_mobile,
                                                                           criteria=pname_mobile_old)
            if item is not None:
                if mobile_number is not None and pnameNew is not None:
                    id = f"{pnameNew}_{mobile_number}"
                    item.setText(id)

    def delete_casesheet(self):
        pass

    def clear_casesheet(self):
        # item = self.List_of_casesheet.currentItem()
        row = self.Holding_List.currentRow()
        item = self.Holding_List.item(row)
        item_name = item.text()

        if item_name == "Others":
            QMessageBox.information(self, 'Clear Failed !!',
                                    f"'{item_name}' cannot be cleared !")
            return

        pname = item_name.split('_')[0]
        mobileNo = item_name.split('_')[1]
        pname_mobile = f"patient_name = '{pname}'  and  mobile_no = '{mobileNo}'"
        # row_data_db = self.payin_table.read_row_by_column_values(criteria=pname_mobile)[0]
        data = self.total_index_details.read_row_by_column_values(criteria=pname_mobile)
        df = pd.DataFrame(data)
        credit_card = "{:.{}f}".format(df["pay_credit_card"].sum(), 3)
        debit_card = "{:.{}f}".format(df["pay_debit_card"].sum(), 3)
        cash_payin = "{:.{}f}".format(df["pay_cash"].sum(), 3)
        unpaid = "{:.{}f}".format(df["pay_unpaid"].sum(), 3)
        eft_payin = "{:.{}f}".format(df["pay_eft"].sum(), 3)
        credit_notes = "{:.{}f}".format(df["credit_note"].sum(), 3)

        total_transaction_reciept = float(cash_payin) + float(credit_card) + float(debit_card) + float(
            eft_payin) + float(credit_notes)
        balance_amount = float(unpaid) - float(total_transaction_reciept)

        if balance_amount > 0.0:
            QMessageBox.information(self, 'Aborted !!',
                                    f'Selected  transaction of {item_name} has not been cleared\nDue amount : Rs. {balance_amount}')
        else:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Warning")
            msgBox.setText(f"Are you sure to clear transaction information of {item_name} from unpaid ?")
            msgBox.setInformativeText(
                f"Unpaid transaction  information will be \npermanatly cleared from the database !")
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgBox.setDefaultButton(QMessageBox.No)
            buttonY = msgBox.button(QMessageBox.Yes)
            buttonY = msgBox.button(QMessageBox.Yes)
            # buttonY.setText('Evet')
            # buttonN = box.button(QtGui.QMessageBox.No)
            # buttonN.setText('Iptal')
            msgBox.exec_()

            if msgBox.clickedButton() == buttonY:
                pname_mobile = f" patient_name = '{pname}'  and  mobile_no = '{mobileNo}' "
                mask1 = self.df_reception_payin["Patient Name"] == pname
                self.df_reception_payin.loc[mask1, ["Unpaid"]] = 0.0
                self.holdingModel.update(self.df_reception_payin, key="Update")
                self.holdingModel.layoutChanged.emit()
                self.holdingTable.clearSelection()
                set_unpaid = f" pay_unpaid = '{0.0}' "

                self.Holding_List.takeItem(row)
                indx = self.Holding_List.count() - 1
                if indx >= 0:
                    item = self.Holding_List.item(indx)
                    self.Holding_List.setCurrentItem(item)

                messge = self.total_index_details.update_rows_by_column_values(set_argument=set_unpaid,
                                                                               criteria=pname_mobile)
                # print(messge)
                QMessageBox.information(self, 'Cleared !!',
                                        f'Selected  transaction of {item_name} has been cleared')
            else:
                # msgBox = QMessageBox()
                # msgBox.setWindowTitle("Aborted")
                # msgBox.setText("Selected  transaction (Serial No: " + billNo + ") has not been deleted")
                # msgBox.setIcon(QMessageBox.Information)
                # msgBox.exec_()
                QMessageBox.information(self, 'Aborted !!',
                                        f'Selected  transaction of {item_name} has not been cleared')

    def calculate_sum(self):
        credit_card = "{:.{}f}".format(self.df_reception_payin["CreditCard"].sum(), 3)
        debit_card = "{:.{}f}".format(self.df_reception_payin["DebitCard"].sum(), 3)
        cash_payin = "{:.{}f}".format(self.df_reception_payin["Cash"].sum(), 3)
        unpaid = "{:.{}f}".format(self.df_reception_payin["Unpaid"].sum(), 3)
        eft_payin = "{:.{}f}".format(self.df_reception_payin["EFT"].sum(), 3)
        credit_notes = "{:.{}f}".format(self.df_reception_payin["CreditNote"].sum(), 3)

        total_transaction_reciept = float(cash_payin) + float(credit_card) + float(debit_card) + float(
            eft_payin) + float(credit_notes)
        balance_amount = float(unpaid) - float(total_transaction_reciept)

        self.credit_card_total.setText(format_currency(credit_card, 'INR', locale='en_IN'))
        self.debit_card_total.setText(format_currency(debit_card, 'INR', locale='en_IN'))
        self.cash_payin.setText(format_currency(cash_payin, 'INR', locale='en_IN'))
        self.unpaid_total.setText(format_currency(unpaid, 'INR', locale='en_IN'))
        self.eft_payin_total.setText(format_currency(eft_payin, 'INR', locale='en_IN'))
        self.credit_note_total.setText(format_currency(credit_notes, 'INR', locale='en_IN'))

        self.total_unpaid_amount.setText(format_currency(unpaid, 'INR', locale='en_IN'))
        self.total_cleared_amount.setText(format_currency(total_transaction_reciept, 'INR', locale='en_IN'))
        self.overall_balance.setText(format_currency(balance_amount, 'INR', locale='en_IN'))

        self.credit_card_total.setStyleSheet('color: blue')
        self.debit_card_total.setStyleSheet('color: blue')
        self.cash_payin.setStyleSheet('color: blue')
        self.unpaid_total.setStyleSheet('color: blue')
        self.eft_payin_total.setStyleSheet('color: blue')
        self.credit_note_total.setStyleSheet('color: green')

        self.total_unpaid_amount.setStyleSheet('color: red')
        self.total_cleared_amount.setStyleSheet('color: green')
        self.overall_balance.setStyleSheet('color: red')

    @pyqtSlot(QPoint)
    def rightClickMenuPayIn(self, pos):
        indexes = self.sender().selectedIndexes()
        mdlIdx = self.holdingTable.indexAt(pos)
        row = self.holdingTable.currentIndex().row()

        if not mdlIdx.isValid() and len(indexes) != 0:
            # print("return")
            return
        elif len(indexes) == 0 and not mdlIdx.isValid():
            # print("new..")
            self.menu_current_portfolio = QMenu(self)
            newAct = QAction(QIcon(""), "New", self, triggered=self.add_new_stock)
            # CloseBalanceAct = QAction(QIcon(""), "Clear Balance and Close a/c", self, triggered=self.clear_and_close)
            # newAct.setShortcut(QKeySequence("Ctrl+N"))
            editStk = self.menu_current_portfolio.addAction(newAct)
            # editStk = self.menu_payin.addAction(CloseBalanceAct)

        else:
            self.menu_current_portfolio = QMenu(self)

            # newAct.setShortcut(QKeySequence("Ctrl+N"))
            historyActSMA = QAction(QIcon(""), "HistorySMA", self,
                                    triggered=self.plot_historySMA)
            historyActEMA = QAction(QIcon(""), "HistoryEMA", self,
                                    triggered=self.plot_historyEMA)
            # newAct = QAction(QIcon(""), "New", self, triggered=self.add_new_stock)
            # editeAct = QAction(QIcon(""), "Edit Bill", self, triggered=self.edit_selected_stock)
            # # duelistAct = QAction(QIcon(""), "Register Unpaid", self, triggered=self.move_to_unpaid_payin)
            # deleteAct = QAction(QIcon(""), "Delete", self, triggered=self.delete_selected_stock)
            # soldAct = QAction(QIcon(""), 'Sold', self, triggered=self.stock_sold)
            # avgAct = QAction(QIcon(""), 'Average', self, triggered=self.stock_avg)
            # CloseBalanceAct = QAction(QIcon(""), "Clear Balance and Close a/c", self, triggered=self.clear_and_close)
            # remAct.setStatusTip('Delete stock from database')
            # showAct = QAction(QIcon(""), 'Show', self, triggered=self.showBill)
            histStk = self.menu_current_portfolio.addAction(historyActSMA)
            histStk = self.menu_current_portfolio.addAction(historyActEMA)
            # addAct = self.menu_current_portfolio.addAction(newAct)
            # editStk = self.menu_current_portfolio.addAction(editeAct)
            # delStk = self.menu_current_portfolio.addAction(deleteAct)
            # avgStk = self.menu_current_portfolio.addAction(avgAct)
            # self.menu_current_portfolio.addSeparator()
            # soldStk = self.menu_current_portfolio.addAction(soldAct)

        self.menu_current_portfolio.exec_(self.sender().viewport().mapToGlobal(pos))

    def plot_historySMA(self):
        self.plot_history()

    def plot_historyEMA(self):
        self.plot_history(moving_avg='EMA')

    def plot_history(self, moving_avg='SMA'):
        # fetch data from mysql
        index = self.holdingTable.currentIndex().row()
        ncol = self.holdingModel.columnCount()
        row_data = []
        for col in range(ncol):
            val = self.holdingTable.model().index(index, col).data()
            row_data.append(val)

        # print(row_data)
        # self.plot_graphs(price=row_data[3], buy_date=row_data[2], symbol=row_data[1])
        self.plot_graphs(moving_avg,buy_date=row_data[0], symbol=row_data[1])

        # item_name = item.text()

    def add_new_stock(self):
        save_db = False
        ref_no = gen_id(**self.db_cfg)

        newBill_inp = new_stock(ref_no)
        if newBill_inp.exec_() == newBill_inp.Accepted:
            new_stock_addition, save_db = list(newBill_inp.get_inp())
            dateNow = str(QDateTime.currentDateTime().toString(DATE_TIME))
            # CURRENT_HOLDING_DB_HEADER = ['id', 'ref_number', 'agency', 'exchange', 'equity', 'buy_date', 'avg_price',
            #                              'quantity', 'remarks']
            #    0      1       2       3       4       5           6           7       8
            # agency, xchange, equity, tdate, price, quantity, chargesEntry, comment, self.save_db
            # TOTAL_HOLDINGS_DB_HEADER = ['id', 'ref_number', 'date', 'type', 'agency', 'equity', 'quantity', 'price',
            # 'fees', 'avg_price', 'current_holding', 'remarks']

            df_row = pd.DataFrame([new_stock_addition])
            listt = list(new_stock_addition.values())
            vals_tuple = [tuple(listt)]
            df_row.columns = TOTAL_HOLDINGS_DB_HEADER
            df_row.drop(CURRENT_HOLDINGS_HEADER_DROP_LIST, axis=1, inplace=True)
            # reorder columns names
            CURRENT_HOLDINGS_HEADER_DB = []
            for hdr_name in CURRENT_HOLDINGS_HEADER_DISPLAY_LIST:
                CURRENT_HOLDINGS_HEADER_DB.append(CURRENT_HOLDINGS_HEADER_DISPLAY_LIST2DB[hdr_name])
            df_row = df_row.loc[:, CURRENT_HOLDINGS_HEADER_DB]
            df_row.columns = CURRENT_HOLDINGS_HEADER_DISPLAY_LIST

            self.index_trend_data_df = pd.concat([df_row, self.index_trend_data_df]).reset_index(drop=True)
            self.holdingModel.update(self.index_trend_data_df, key="New")
            self.holdingModel.layoutChanged.emit()
            self.holdingTable.clearSelection()

            if save_db:
                messge = self.total_index_details.insert_row_by_column_values(row_val=vals_tuple)

            # self.calculate_sum()

    # def updateBill_payin(self):
    #     self.modify_payin_bill(BILL_MODIFY_TYPE[0])

    def edit_selected_stock(self):
        self.modify_stock_details()

    def modify_stock_details(self, balance_amount=None):
        # fetch data from mysql
        index = self.holdingTable.currentIndex().row()
        ncol = self.holdingModel.columnCount()
        row_data = []
        for col in range(ncol):
            val = self.holdingTable.model().index(index, col).data()
            row_data.append(val)

        edit_stock = make_nested_dict()
        for key in TOTAL_HOLDINGS_DB_HEADER:
            edit_stock[key] = None
        search_item = f"ref_number = {row_data[0]}"
        row_data_db = self.total_index_details.read_row_by_column_values(criteria=search_item)[0]

        # print(row_data)
        # print(row_data_db)
        if row_data_db['ref_number'] != '':
            editBill_inp = edit_selected_stock(row_data_db)
            if editBill_inp.exec_() == editBill_inp.Accepted:
                edit_stock_details, save_db = editBill_inp.get_inp()

                # print("update val --> ", set_list)
                # https: // stackoverflow.com / questions / 21608228 / conditional - replace - pandas
                # https: // stackoverflow.com / questions / 36909977 / update - row - values - where - certain - condition - is -met - in -pandas / 36910033

                mask1 = self.index_trend_data_df["Reference"] == row_data_db['ref_number']
                for k, v in edit_stock_details.items():
                    key = CURRENT_HOLDING_DB_TO_DISPLAY[k]
                    if key in self.index_trend_data_df.columns.values.tolist() and key != 'Reference':
                        self.index_trend_data_df.loc[mask1, key] = edit_stock_details[k]

                self.holdingModel.update(self.index_trend_data_df, key="New")
                self.holdingModel.layoutChanged.emit()
                self.holdingTable.clearSelection()

                if save_db:
                    set_list = ""
                    for k, v in edit_stock_details.items():
                        if k != 'id':
                            set_list = f"{set_list},{k}='{v}'"
                    set_list = set_list[1:]
                    messge = self.total_index_details.update_rows_by_column_values(set_argument=set_list,
                                                                                   criteria=f"ref_number='{row_data_db['ref_number']}'")
                    # print(set_list)
                    # print(messge)

                # self.calculate_sum()
            # else:
            #     QMessageBox.information(self, 'Insufficient data !!',
            #                             f'Insufficient data in selected  transaction/bill..')

    def delete_selected_stock(self):
        # fetch data from mysql
        index = self.holdingTable.currentIndex().row()
        ncol = self.holdingModel.columnCount()
        row_data = []
        for col in range(ncol):
            val = self.holdingTable.model().index(index, col).data()
            row_data.append(val)

        if row_data[0] != '':
            search_item = f"ref_number = {row_data[0]}"
            row_data_db = self.total_index_details.read_row_by_column_values(criteria=search_item)[0]
            ref_number = row_data_db['ref_number']
            equity = row_data_db['equity']
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Warning")
            msgBox.setText(f"Are you sure to delete equity {equity} data ref. no. {ref_number} ?")
            msgBox.setInformativeText(f"Equity  information will be \npermanatly removed from the database !")
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgBox.setDefaultButton(QMessageBox.No)
            buttonY = msgBox.button(QMessageBox.Yes)
            buttonY = msgBox.button(QMessageBox.Yes)
            # buttonY.setText('Evet')
            # buttonN = box.button(QtGui.QMessageBox.No)
            # buttonN.setText('Iptal')
            msgBox.exec_()

            if msgBox.clickedButton() == buttonY:
                message = self.total_index_details.delete_row_by_column_values(criteria=search_item)
                mask1 = self.index_trend_data_df["Reference"] == int(row_data[0])
                index = self.index_trend_data_df[mask1].index
                self.index_trend_data_df.drop(index, axis=0, inplace=True)
                self.holdingModel.update(self.index_trend_data_df, key="Delete")
                self.holdingModel.layoutChanged.emit()
                self.holdingTable.clearSelection()
                QMessageBox.information(self, 'Deleted !!',
                                        f'Selected  equity (Ref. No:{row_data[0]}) has been deleted')
            else:
                QMessageBox.information(self, 'Aborted !!',
                                        f'Selected  equity (Ref. No:{row_data[0]}) has not been deleted')

            # self.calculate_sum()
        else:
            QMessageBox.information(self, 'Insufficient data !!',
                                    f'Insufficient data in selected equity..')

    def stock_sold(self):
        # fetch data from mysql
        index = self.holdingTable.currentIndex().row()
        ncol = self.holdingModel.columnCount()
        # new_stock_addition = make_nested_dict()
        row_data = []
        for col in range(ncol):
            val = self.holdingTable.model().index(index, col).data()
            row_data.append(val)

        search_item = f"ref_number = {row_data[0]}"
        row_data_db = self.total_index_details.read_row_by_column_values(criteria=search_item)[0]

        # print(row_data)
        # print(row_data_db)
        old_price = parse_str(row_data_db['avg_price'])
        old_quantity = parse_str(row_data_db['quantity'])

        if row_data_db['ref_number'] != '':
            sell_stock_inp = sell_selected_stock(row_data_db)
            if sell_stock_inp.exec_() == sell_stock_inp.Accepted:
                sell_stock_details, save_db = sell_stock_inp.get_inp()
                balance_quantity = int(old_quantity) - int(sell_stock_details['quantity'])
                if balance_quantity > 0:
                    # updating latest changes to gui table
                    row_data_db['quantity'] = balance_quantity
                    mask1 = self.index_trend_data_df["Reference"] == row_data_db['ref_number']
                    for k, v in row_data_db.items():
                        key = CURRENT_HOLDING_DB_TO_DISPLAY[k]
                        if key in self.index_trend_data_df.columns.values.tolist() and key != 'Reference':
                            self.index_trend_data_df.loc[mask1, key] = row_data_db[k]

                    self.holdingModel.update(self.index_trend_data_df, key="New")
                    self.holdingModel.layoutChanged.emit()
                    self.holdingTable.clearSelection()

                    # updating latest changes to database
                    if save_db:
                        set_list = f"quantity = '{balance_quantity}'"
                        messge = self.total_index_details.update_rows_by_column_values(set_argument=set_list,
                                                                                       criteria=f"ref_number='{row_data_db['ref_number']}'")
                    # adding sold quantities to database
                    if save_db:
                        sell_stock_details['ref_number'] = gen_id(**self.db_cfg)
                        listt = list(sell_stock_details.values())
                        vals_tuple = [tuple(listt)]
                        messge = self.total_index_details.insert_row_by_column_values(row_val=vals_tuple)
                        print(messge)
                elif balance_quantity == 0:
                    if save_db:
                        set_list = f"current_holding = '{0}'"
                        messge = self.total_index_details.update_rows_by_column_values(set_argument=set_list,
                                                                                       criteria=f"ref_number='{row_data_db['ref_number']}'")
                        sell_stock_details['ref_number'] = gen_id(**self.db_cfg)
                        listt = list(sell_stock_details.values())
                        vals_tuple = [tuple(listt)]
                        messge = self.total_index_details.insert_row_by_column_values(row_val=vals_tuple)
                        # print(messge)
                        mask1 = self.index_trend_data_df["Reference"] == int(row_data[0])
                        index = self.index_trend_data_df[mask1].index
                        self.index_trend_data_df.drop(index, axis=0, inplace=True)
                        self.holdingModel.update(self.index_trend_data_df, key="Delete")
                        self.holdingModel.layoutChanged.emit()
                        self.holdingTable.clearSelection()
                else:
                    QMessageBox.information(self, 'Balance quantity incorrect !!',
                                            f"Available stock is only {old_quantity}.\nYou have tried to sell {sell_stock_details['quantity']}")


    def stock_avg(self):
        index = self.holdingTable.currentIndex().row()
        ncol = self.holdingModel.columnCount()
        row_data = []
        for col in range(ncol):
            val = self.holdingTable.model().index(index, col).data()
            row_data.append(val)

        edit_stock = make_nested_dict()
        for key in TOTAL_HOLDINGS_DB_HEADER:
            edit_stock[key] = None
        search_item = f"ref_number = {row_data[0]}"
        row_data_db = self.total_index_details.read_row_by_column_values(criteria=search_item)[0]
        print(row_data_db)

        if row_data[0] != "":
            showInfo = average_stocks(row_data_db)
            showInfo.exec_()


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    mysql_data={'user': 'kiran', 'passwd': 'pass1word', 'port': 3306, 'host': 'localhost', 'db': 'stock_database'}
    super_trend = indexes_display(**mysql_data)
    # super_trend.show()
    super_trend.showMaximized()
    # if gui_switch.exec_() == gui_switch.Accepted:
    #     plot_all_data = gui_switch.get_inp()
    #     print("Plot all data ?",plot_all_data)

    sys.exit(app.exec_())
