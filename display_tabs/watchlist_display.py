import pandas as pd

from PyQt5 import QtWebEngineWidgets
from PyQt5.QtCore import Qt, QPoint, pyqtSlot
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QWidget, QMenu, QAction, QTableView, \
    QMessageBox, \
    QVBoxLayout, QHBoxLayout, QGroupBox, \
    QAbstractItemView, \
    QHeaderView, QSplitter

# from babel.numbers import format_currency
import datetime

from mysql_tools.mysql_crud import mysql_table_crud
from mysql_tools.tables_and_headers import WATCHLIST_DISPLAY, \
    WATCHLIST_DB_HEADER, WATCHLIST_HEADER_DISPLAY_LIST2DB,WATCHLIST_DB_TABLE_NAME, \
    WATCHLIST_HEADER_DISPLAY_LIST,WATCHLIST_HEADER_DROP_LIST

from gui_widgets.gui_widgets_for_adding_watchlist_stock  import \
     add_watchlist_stock

# from DataBase.mysql_crud import mysql_table_crud
from utility.tableViewModel import pandasModel
from utility.fonts_style import TABLE_HEADER_FONT, TABLE_FONT
from utility.utility_functions import make_nested_dict
from os.path import expanduser
from utility.date_time import DATE_FMT_YMD, DATE_FMT_DMY
from utility.utility_functions import gen_id, \
    symbol_date_string, create_watchlist_csv_file_names

from share.libnames import EMA_YEARS, SMA_YEARS

from display_tabs.utility_display_tab import get_current_holdings_history_mp

from plotly import graph_objs as go
from plotly.subplots import make_subplots
# from plotly.tools import make_subplots
from ta.trend import MACD
from ta.momentum import StochasticOscillator

global DEFAULT_PATH
usr_path = expanduser("~")
DEFAULT_PATH = f"{usr_path}/Desktop/"


class watchlist_display_tab(QWidget):
    def __init__(self, **mysql_data):
        super().__init__()
        # self.setWindowTitle("Balance test")
        self.db_cfg = mysql_data
        self.UI()

    def UI(self):
        self.connect_to_tables()
        self.get_watchlist_data()
        self.widgets()
        # print('widgets')
        self.layouts()

    def get_watchlist_data(self):
        self.watchlist_data_df = self.get_watchlist_details()
        #
        self.watchlist_history = self.extract_watchlist_history()
        # print(self.watchlist_history.keys())

    def widgets(self):
        self.data_plot_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.watchlist_data_df.columns = WATCHLIST_HEADER_DISPLAY_LIST
        self.holdingModel, self.holdingTable = self.tableViewDataModel(
            self.watchlist_data_df)
        self.holdingModel.sort(1, Qt.DescendingOrder)
        self.holdingTable.installEventFilter(self)
        # self.holdingTable.hideColumn(0)
        self.holdingTable.setColumnHidden(0, True)
        self.holdingTable.setColumnHidden(2, True)
        self.holdingTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.holdingTable.customContextMenuRequested.connect(
            self.rightClickMenuPayIn)

    def connect_to_tables(self):
        self.total_watchlist_details = mysql_table_crud(
            db_table=WATCHLIST_DB_TABLE_NAME,
            db_header=WATCHLIST_DB_HEADER,
            **self.db_cfg)

    def get_watchlist_details(self):
        data = make_nested_dict()
        for col in WATCHLIST_DB_HEADER:
            data[col] = None
        data = self.total_watchlist_details.read_row_by_column_values()
        symbol_df = pd.DataFrame(data)
        symbol_df = symbol_df.loc[:, WATCHLIST_DISPLAY]
        return symbol_df

    def extract_watchlist_history(self):
        current_holdings_csv_file_names = create_watchlist_csv_file_names(
            self.watchlist_data_df)
        return get_current_holdings_history_mp(current_holdings_csv_file_names)

    def layouts(self):
        self.mainLayout = QHBoxLayout()
        self.horizontalSplitter = QSplitter(Qt.Horizontal)
        self.leftVsplitter = QSplitter(Qt.Vertical)
        self.rightVsplitter = QSplitter(Qt.Vertical)
        self.rightBottomLayout = QHBoxLayout()

        self.leftLayout = QVBoxLayout()
        self.rightLayout = QVBoxLayout()
        self.leftTopGroupBox = QGroupBox("Watchlist")
        self.rightTopGroupBox = QGroupBox("Script Information")

        # self.rightBottomWidget = QWidget()
        # self.rightBottomWidget.setLayout(self.rightBottomLayout)
        self.leftLayout.addWidget(self.holdingTable)
        ncol = self.holdingModel.columnCount()
        row_data = []
        for col in range(ncol):
            val = self.holdingTable.model().index(0, col).data()
            row_data.append(val)

        self.plot_graphs(moving_avg='SMA',
                         buy_date=row_data[2], symbol=row_data[1])
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

    def plot_graphs(self, moving_avg, buy_date=datetime.date.today()
                    , symbol="DMART"):
        # https: // stackoverflow.com / questions / 47797383 / plotly - legend - next - to - each - subplot - python
        # buy_date = pd.to_datetime(buy_date).date()
        # print(type(buy_date),buy_date)

        if symbol == 'None':
            fig = make_subplots(rows=1, cols=1,
                                vertical_spacing=0.01,
                                shared_xaxes=True)
            # df=pd.DataFrame(dummy_stock_history)
            self.data_plot_browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
            return

        buy_date = datetime.datetime.strptime(buy_date, DATE_FMT_DMY)
        buy_date = datetime.datetime.strftime(buy_date, DATE_FMT_YMD)
        # buy_date = datetime.datetime.strptime(buy_date, DATE_FMT_YMD)
        symbol_buy_date = symbol_date_string(symbol, buy_date)
        # print(symbol_buy_date)
        try:
            df = self.watchlist_history[symbol_buy_date]
            df['Date'] = pd.to_datetime(df['Date']).dt.date
        except FileNotFoundError:
            QMessageBox.information(self, f'{symbol} history missing !!',
                                    f'Please download stock history of {symbol} ')
            return

        if len(df) == 0:
            QMessageBox.information(self, f'{symbol} history missing !!',
                                    f'Please download stock history of '
                                    f'{symbol} or\n{symbol} name itself may '
                                    f'be wrong '
                                    f'!! ')
            return

        if moving_avg == 'EMA':
            start_date = datetime.date.today() - datetime.timedelta(
                EMA_YEARS * 365)
            mask = df['Date'] > start_date
            df = df.loc[mask].copy()
            start_date0 = df['Date'].iloc[0]
        elif moving_avg == 'SMA':
            start_date = datetime.date.today() - datetime.timedelta(
                SMA_YEARS * 365)
            # df['Date']=pd.to_datetime(df['Date']).dt.date
            mask = df['Date'] > start_date
            df = df.loc[mask].copy()
            # print(df.head().to_string())
            start_date0 = df['Date'].iloc[0]

        # print(start_date0,'>',start_date)
        if start_date0 > start_date:
            start_date = start_date0

        end_date = datetime.date.today() + datetime.timedelta(30)
        # dummy_row={'Date':delta_time ,'Open':None, 'Close':None, 'High':None, 'Low':None, \
        #           'Adj Close':None, 'Volume':None}
        # df=df.append(dummy_row,ignore_index=True)

        if len(df) == 0:
            QMessageBox.information(self, f'{symbol} history missing !!',
                                    f'Please download stock history of {symbol} ')
            return

        # exit()
        if symbol_buy_date in self.watchlist_history.keys() and not \
                self.watchlist_history[
                    symbol_buy_date].empty:
            # if symbol in self.holding_history.keys() and len(df) != 0 and :
            # df = self.current_holding_history[symbol_buy_date]
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
            dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if
                         not d in dt_obs]
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
                sma_dict = {'SMA20': [20, 'black'], 'SMA44': [44, 'coral'],
                            'SMA50': [50, 'blue'], 'SMA100': [100, 'green'],
                            'SMA200': [200, 'red']}

                for sma, val in sma_dict.items():
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
                    df[ema] = df['Close'].ewm(span=val[0], adjust=False,
                                              min_periods=1).mean()
                    fig.add_trace(go.Scatter(x=df['Date'],
                                             y=df[ema],
                                             opacity=0.7,
                                             line=dict(color=val[1], width=2),
                                             name=ema))
            elif moving_avg == 'CMA':
                df['MA20'] = df['Close'].rolling(window=20,
                                                 min_periods=1).mean()

            # fig.add_hline(y=price, line_width=2, line_color="red", opacity=0.7,
            #               name='Buy Avg.')

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
            # fig.update_xaxes(minor=[dict(showgrid=True)])
            # fig.update_xaxes(minor=dict(showgrid=True))
            fig.update_xaxes(minor_showgrid=True)
            # fig.update_xaxes(showgrid=True)
            # fig.update_yaxes(minor=showgrid=True))
            # remove rangeslider
            # fig.update_layout(xaxis_rangeslider_visible=False)
            # # add chart title
            fig.update_layout(title=symbol)
            fig.update_layout(xaxis=dict(range=[start_date, end_date]))

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


    @pyqtSlot(QPoint)
    def rightClickMenuPayIn(self, pos):
        indexes = self.sender().selectedIndexes()
        mdlIdx = self.holdingTable.indexAt(pos)
        row = self.holdingTable.currentIndex().row()

        if not mdlIdx.isValid() and len(indexes) != 0:
            return
        elif len(indexes) == 0 and not mdlIdx.isValid():
            self.menu_current_portfolio = QMenu(self)
            newAct = QAction(QIcon(""), "New", self,
                             triggered=self.add_new_stock)
            editStk = self.menu_current_portfolio.addAction(newAct)

        else:
            self.menu_current_portfolio = QMenu(self)

            # newAct.setShortcut(QKeySequence("Ctrl+N"))
            historyActSMA = QAction(QIcon(""), "HistorySMA", self,
                                    triggered=self.plot_historySMA)
            historyActEMA = QAction(QIcon(""), "HistoryEMA", self,
                                    triggered=self.plot_historyEMA)
            # historyActCMA = QAction(QIcon(""), "HistoryCMA", self,
            #                         triggered=self.plot_historyCMA)
            newAct = QAction(QIcon(""), "New", self,
                             triggered=self.add_new_stock)
            # duelistAct = QAction(QIcon(""), "Register Unpaid", self, triggered=self.move_to_unpaid_payin)
            deleteAct = QAction(QIcon(""), "Delete", self,
                                triggered=self.delete_selected_stock)

            histStk1 = self.menu_current_portfolio.addAction(historyActSMA)
            histStk2 = self.menu_current_portfolio.addAction(historyActEMA)
            # histStk3 = self.menu_current_portfolio.addAction(historyActCMA)
            addAct = self.menu_current_portfolio.addAction(newAct)
            delStk = self.menu_current_portfolio.addAction(deleteAct)

        self.menu_current_portfolio.exec_(
            self.sender().viewport().mapToGlobal(pos))

    def plot_historySMA(self):
        self.plot_history()

    def plot_historyEMA(self):
        self.plot_history(moving_avg='EMA')

    def plot_historyCMA(self):
        self.plot_history(moving_avg='CMA')

    def plot_history(self, moving_avg='SMA'):
        # fetch data from mysql
        index = self.holdingTable.currentIndex().row()
        ncol = self.holdingModel.columnCount()
        row_data = []
        for col in range(ncol):
            val = self.holdingTable.model().index(index, col).data()
            row_data.append(val)

        # print(row_data)
        self.plot_graphs(moving_avg, buy_date=row_data[2], symbol=row_data[1])

        # item_name = item.text()

    def add_new_stock(self):
        save_db = False
        ref_no = gen_id(**self.db_cfg)

        newBill_inp = add_watchlist_stock(ref_no)
        if newBill_inp.exec_() == newBill_inp.Accepted:
            new_stock_addition, save_db = list(newBill_inp.get_inp())
            df_row = pd.DataFrame([new_stock_addition])
            df_row.columns = WATCHLIST_DB_HEADER
            df_row.drop(WATCHLIST_HEADER_DROP_LIST, axis=1, inplace=True)
            # reorder columns names
            WATCHLIST_HEADER_DB = []
            for hdr_name in WATCHLIST_HEADER_DISPLAY_LIST:
                WATCHLIST_HEADER_DB.append(
                    WATCHLIST_HEADER_DISPLAY_LIST2DB[hdr_name])

            df_row = df_row.loc[:, WATCHLIST_HEADER_DB]
            df_row.columns = WATCHLIST_HEADER_DISPLAY_LIST
            self.watchlist_data_df.columns=WATCHLIST_HEADER_DISPLAY_LIST

            self.watchlist_data_df = pd.concat(
                [df_row, self.watchlist_data_df]).reset_index(drop=True)
            self.holdingModel.update(self.watchlist_data_df, key="New")

            if save_db:
                listt = list(new_stock_addition.values())
                vals_tuple = [tuple(listt)]
                messge = self.total_watchlist_details.insert_row_by_column_values(
                    row_val=vals_tuple)

            # print(self.watchlist_data_df)
            self.get_watchlist_data()
            # print(self.watchlist_data_df)
            # print(self.watchlist_history)


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
            row_data_db = self.total_watchlist_details.read_row_by_column_values(
                criteria=search_item)[0]
            ref_number = row_data_db['ref_number']
            equity = row_data_db['equity']
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Warning")
            msgBox.setText(
                f"Are you sure to delete equity {equity} data ref. no. {ref_number} ?")
            msgBox.setInformativeText(
                f"Equity  information will be \npermanatly removed from the database !")
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
                message = self.total_watchlist_details.delete_row_by_column_values(
                    criteria=search_item)
                mask1 = self.watchlist_data_df["Reference"] == int(
                    row_data[0])
                index = self.watchlist_data_df[mask1].index
                self.watchlist_data_df.drop(index, axis=0, inplace=True)
                self.holdingModel.update(self.watchlist_data_df,
                                         key="Delete")
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



if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    mysql_data = {'user': 'kiran', 'passwd': 'pass1word', 'port': 3306,
                  'host': 'localhost', 'db': 'stock_database'}
    super_trend = watchlist_display_tab(**mysql_data)
    # super_trend.show()
    super_trend.showMaximized()
    # if gui_switch.exec_() == gui_switch.Accepted:
    #     plot_all_data = gui_switch.get_inp()
    #     print("Plot all data ?",plot_all_data)

    sys.exit(app.exec_())
