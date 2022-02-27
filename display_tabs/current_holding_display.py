import copy
import os
import pandas as pd

from PyQt5 import QtWebEngineWidgets
from PyQt5.QtCore import Qt, QPoint, pyqtSlot, QTimer, QDateTime
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QWidget, QListWidget, QMenu, QAction, QTableView, QLabel, QMessageBox, \
    QVBoxLayout, QHBoxLayout, QGroupBox, \
    QGridLayout, QAbstractItemView, \
    QHeaderView, QSplitter, QFileDialog

# from babel.numbers import format_currency
import datetime
import yfinance as yf

from mysql_tools.mysql_crud import mysql_table_crud
from mysql_tools.tables_and_headers import CURRENT_HOLDINGS_DB_TABLE_NAME
from utility.libnames import PATH_TO_DATABASE_CURRENT_HOLDINGS
from mysql_tools.tables_and_headers import  CURRENT_HOLDING_LIST_DISPLAY, \
    CURRENT_HOLDING_DB_TO_DISPLAY, CURRENT_HOLDINGS_HEADER_DROP_LIST, CURRENT_HOLDINGS_HEADER_DISPLAY_LIST, \
    TOTAL_HOLDINGS_DB_TABLE_NAME, TOTAL_HOLDINGS_DB_HEADER

from gui_widgets.gui_widgets_for_adding_new_stock import add_new_stock as new_stock
from gui_widgets.gui_widgets_for_editing_selected_stock import edit_selected_stock
from gui_widgets.gui_widgets_for_selling_selected_stock import sell_selected_stock
from gui_widgets.gui_widgets_average_stocks import average_stocks

import copy
# from DataBase.mysql_crud import mysql_table_crud
from utility.tableViewModel import pandasModel
from utility.fonts_style import TABLE_HEADER_FONT, TABLE_FONT
from utility.utility_functions import gen_id, make_nested_dict, parse_str, weighted_average, get_nested_dist_value
from os.path import expanduser
from utility.date_time import DATE_TIME, DATE_FMT_YMD, DATE_FMT_DMY
from utility.utility_functions import reduce_mem_usage, symbol_date_range_string, date_symbol_split, gen_id,\
    symbol_date_string,create_current_holdings_csv_file_names,create_sold_holdings_csv_file_names,symbol_date_split

from display_tabs.utility_diaplay_tab import get_current_holdings_history


import plotly.express as px
from plotly import graph_objs as go
from plotly.subplots import make_subplots
# from plotly.tools import make_subplots
from ta.trend import MACD
from ta.momentum import StochasticOscillator

global DEFAULT_PATH
usr_path = expanduser("~")
DEFAULT_PATH = f"{usr_path}/Desktop/"


class list_of_holdings_display(QWidget):
    def __init__(self, **mysql_data):
        super().__init__()
        # self.setWindowTitle("Balance test")
        self.db_cfg = mysql_data
        self.UI()

    def UI(self):
        self.connect_to_tables()

        self.current_holding_data_df = self.get_current_holdings_details()
        # print(self.current_holding_data_df.head(10).to_string())
        #
        self.current_holding_history = self.extract_current_holdings_history()
        # print(self.current_holding_history.keys())
        # exit()

        self.widgets()
        self.layouts()

    def widgets(self):
        self.data_plot_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.current_holding_data_df.columns = CURRENT_HOLDINGS_HEADER_DISPLAY_LIST
        self.holdingModel, self.holdingTable = self.tableViewDataModel(self.current_holding_data_df)
        self.holdingModel.sort(1, Qt.DescendingOrder)
        self.holdingTable.installEventFilter(self)
        self.holdingTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.holdingTable.customContextMenuRequested.connect(self.rightClickMenuPayIn)

    def connect_to_tables(self):
        self.total_holdings_details = mysql_table_crud(db_table=TOTAL_HOLDINGS_DB_TABLE_NAME,
                                                       db_header=TOTAL_HOLDINGS_DB_HEADER,
                                                       **self.db_cfg)

    def get_current_holdings_details(self):
        data = self.total_holdings_details.read_row_by_column_values()
        df = pd.DataFrame(data)
        mask = df["current_holding"] == True
        symbol_df = df.loc[mask].copy()

        # required_columns=['ref_number','equity', 'date', 'avg_price', 'quantity']
        # ['Reference', 'Equity', 'Buy Date', 'Avg. Price', 'Quantity']
        # CURRENT_HOLDING_LIST_DISPLAY
        symbol_df=symbol_df.loc[:,CURRENT_HOLDING_LIST_DISPLAY]
        # symbol_df.columns = CURRENT_HOLDINGS_HEADER_DISPLAY_LIST

        return symbol_df

    def extract_current_holdings_history(self):
        return get_current_holdings_history(self.current_holding_data_df)

    def layouts(self):
        self.mainLayout = QHBoxLayout()
        self.horizontalSplitter = QSplitter(Qt.Horizontal)
        self.leftVsplitter = QSplitter(Qt.Vertical)
        self.rightVsplitter = QSplitter(Qt.Vertical)
        self.rightBottomLayout = QHBoxLayout()

        self.leftLayout = QVBoxLayout()
        self.rightLayout = QVBoxLayout()
        self.leftTopGroupBox = QGroupBox("Current Holdings")
        self.rightTopGroupBox = QGroupBox("Script Information")

        # self.rightBottomWidget = QWidget()
        # self.rightBottomWidget.setLayout(self.rightBottomLayout)
        self.leftLayout.addWidget(self.holdingTable)
        ncol = self.holdingModel.columnCount()
        row_data = []
        for col in range(ncol):
            val = self.holdingTable.model().index(0, col).data()
            row_data.append(val)

        # self.plot_graphs()
        self.plot_graphs(price=row_data[3], buy_date=row_data[2], symbol=row_data[1])
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
        self.horizontalSplitter.setStretchFactor(0, 12)
        self.horizontalSplitter.setStretchFactor(1, 88)
        self.horizontalSplitter.setContentsMargins(0, 0, 0, 0)
        self.horizontalSplitter.handle(0)

        self.mainLayout.addWidget(self.horizontalSplitter)
        self.setLayout(self.mainLayout)

    def plot_graphs(self, price=100, buy_date=datetime.date.today(), symbol="DMART"):
        # https: // stackoverflow.com / questions / 47797383 / plotly - legend - next - to - each - subplot - python
        # buy_date = pd.to_datetime(buy_date).date()
        # print(type(buy_date),buy_date)
        buy_date = datetime.datetime.strptime(buy_date, DATE_FMT_DMY)
        buy_date = datetime.datetime.strftime(buy_date, DATE_FMT_YMD)
        # buy_date = datetime.datetime.strptime(buy_date, DATE_FMT_YMD)
        symbol_buy_date = symbol_date_string(symbol,buy_date)
        # print(symbol_buy_date)
        df = self.current_holding_history[symbol_buy_date]
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
        if symbol_buy_date in self.current_holding_history.keys() and not self.current_holding_history[symbol_buy_date].empty:
            # if symbol in self.holding_history.keys() and len(df) != 0 and :
            df = self.current_holding_history[symbol_buy_date]
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
            df['MA20'] = df['Close'].rolling(window=20, min_periods=1).mean()
            df['MA50'] = df['Close'].rolling(window=50, min_periods=1).mean()
            df['MA100'] = df['Close'].rolling(window=100, min_periods=1).mean()
            df['MA200'] = df['Close'].rolling(window=200, min_periods=1).mean()
            # df['MA5'] = df['Close'].rolling(window=5).mean()
            # avg_20 = df.Close.rolling(window=20, min_periods=1).mean()

            fig.add_trace(go.Scatter(x=df['Date'],
                                     y=df['MA20'],
                                     opacity=0.7,
                                     line=dict(color='black', width=2),
                                     name='SMA 20'))
            fig.add_trace(go.Scatter(x=df['Date'],
                                     y=df['MA50'],
                                     opacity=0.7,
                                     line=dict(color='blue', width=2),
                                     name='SMA 50'))
            fig.add_trace(go.Scatter(x=df['Date'],
                                     y=df['MA100'],
                                     opacity=0.7,
                                     line=dict(color='green', width=2),
                                     name='SMA 100'))
            fig.add_trace(go.Scatter(x=df['Date'],
                                     y=df['MA200'],
                                     opacity=0.7,
                                     line=dict(color='red', width=2),
                                     name='SMA 200'))
            fig.add_hline(y=price, line_width=2, line_color="red", opacity=0.7, name='Buy Avg.')

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
            messge = self.total_holdings_details.update_rows_by_column_values(set_argument=pname_mobile,
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
        data = self.total_holdings_details.read_row_by_column_values(criteria=pname_mobile)
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

                messge = self.total_holdings_details.update_rows_by_column_values(set_argument=set_unpaid,
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
            historyAct = QAction(QIcon(""), "History", self, triggered=self.plot_history)
            newAct = QAction(QIcon(""), "New", self, triggered=self.add_new_stock)
            editeAct = QAction(QIcon(""), "Edit Bill", self, triggered=self.edit_selected_stock)
            # duelistAct = QAction(QIcon(""), "Register Unpaid", self, triggered=self.move_to_unpaid_payin)
            deleteAct = QAction(QIcon(""), "Delete", self, triggered=self.delete_selected_stock)
            soldAct = QAction(QIcon(""), 'Sold', self, triggered=self.stock_sold)
            avgAct = QAction(QIcon(""), 'Average', self, triggered=self.stock_avg)
            # CloseBalanceAct = QAction(QIcon(""), "Clear Balance and Close a/c", self, triggered=self.clear_and_close)
            # remAct.setStatusTip('Delete stock from database')
            # showAct = QAction(QIcon(""), 'Show', self, triggered=self.showBill)
            histStk = self.menu_current_portfolio.addAction(historyAct)
            addAct = self.menu_current_portfolio.addAction(newAct)
            editStk = self.menu_current_portfolio.addAction(editeAct)
            delStk = self.menu_current_portfolio.addAction(deleteAct)
            avgStk = self.menu_current_portfolio.addAction(avgAct)
            self.menu_current_portfolio.addSeparator()
            soldStk = self.menu_current_portfolio.addAction(soldAct)

        self.menu_current_portfolio.exec_(self.sender().viewport().mapToGlobal(pos))

    def plot_history(self):
        # fetch data from mysql
        index = self.holdingTable.currentIndex().row()
        ncol = self.holdingModel.columnCount()
        row_data = []
        for col in range(ncol):
            val = self.holdingTable.model().index(index, col).data()
            row_data.append(val)

        # print(row_data)
        self.plot_graphs(price=row_data[3], buy_date=row_data[2], symbol=row_data[1])

        # item_name = item.text()

    def add_new_stock(self):
        save_db = False
        ref_no = gen_id(**self.db_cfg)
        # print(ref_no)
        new_stock_addition = make_nested_dict()

        newBill_inp = new_stock()
        if newBill_inp.exec_() == newBill_inp.Accepted:
            newBill_row = list(newBill_inp.get_inp())
            dateNow = str(QDateTime.currentDateTime().toString(DATE_TIME))
            # CURRENT_HOLDING_DB_HEADER = ['id', 'ref_number', 'agency', 'exchange', 'equity', 'buy_date', 'avg_price',
            #                              'quantity', 'remarks']
            #    0      1       2       3       4       5           6           7       8
            # agency, xchange, equity, tdate, price, quantity, chargesEntry, comment, self.save_db
            new_stock_addition['id'] = 0
            new_stock_addition['ref_number'] = str(ref_no)
            new_stock_addition['agency'] = newBill_row[0]
            new_stock_addition['exchange'] = newBill_row[1]
            new_stock_addition['equity'] = newBill_row[2]
            # new_stock_addition['buy_date'] = dateparser.parse(dateNow)
            new_stock_addition['buy_date'] = dateNow
            new_stock_addition['avg_price'] = round(
                float(newBill_row[4]) + float(newBill_row[6]) / float(newBill_row[5]), 2)
            new_stock_addition['quantity'] = newBill_row[5]
            charges = newBill_row[6]
            new_stock_addition['remarks'] = newBill_row[7]
            save_db = newBill_row[8]

            df_row = pd.DataFrame([new_stock_addition])
            listt = list(new_stock_addition.values())
            vals_tuple = [tuple(listt)]
            df_row.columns = CURRENT_HOLDING_DB_HEADER
            # df_row = df_row.drop(columns=['ID', 'User', 'Edit Info', "Mobile Number"])

            if save_db:
                messge = self.total_holdings_details.insert_row_by_column_values(row_val=vals_tuple)

            df_row.drop(CURRENT_HOLDINGS_HEADER_DROP_LIST, axis=1, inplace=True)
            df_row.columns = CURRENT_HOLDINGS_HEADER_DISPLAY_LIST
            self.current_holding_data_df = pd.concat([df_row, self.current_holding_data_df]).reset_index(drop=True)
            self.holdingModel.update(self.current_holding_data_df, key="New")
            self.holdingModel.layoutChanged.emit()
            self.holdingTable.clearSelection()

            # self.calculate_sum()

    # def updateBill_payin(self):
    #     self.modify_payin_bill(BILL_MODIFY_TYPE[0])

    def edit_selected_stock(self):
        self.modify_stock_details()

    def modify_stock_details(self, balance_amount=None):
        # fetch data from mysql
        index = self.holdingTable.currentIndex().row()
        ncol = self.holdingModel.columnCount()
        new_stock_addition = make_nested_dict()
        row_data = []
        for col in range(ncol):
            val = self.holdingTable.model().index(index, col).data()
            row_data.append(val)

        search_item = f"ref_number = {row_data[0]}"
        row_data_db = self.total_holdings_details.read_row_by_column_values(criteria=search_item)[0]

        # print(row_data)
        # print(row_data_db)

        if row_data_db['ref_number'] != '':
            editBill_inp = edit_selected_stock(row_data_db)
            if editBill_inp.exec_() == editBill_inp.Accepted:
                newBill_row = editBill_inp.get_inp()
                # print("#", newBill_row)
                # "ID", "Reference", "Agency", "Exchange", "Equity", "Buy Date", "Avg. Price", "Quantity",
                # "Remarks"
                new_stock_addition['id'] = 0
                new_stock_addition['ref_number'] = str(row_data_db['ref_number'])
                new_stock_addition['agency'] = newBill_row[0]
                new_stock_addition['exchange'] = newBill_row[1]
                new_stock_addition['equity'] = newBill_row[2]
                # new_stock_addition['buy_date'] = dateparser.parse(dateNow)
                date_time = datetime.datetime.strptime(newBill_row[3], DATE_FMT_DMY)
                # date_time = datetime.strftime(date_time, DATE_FMT_YMD)
                # datetime = datetime.datetime.strptime(input, format)
                new_stock_addition['buy_date'] = date_time.date()  # newBill_row[3]
                new_stock_addition['avg_price'] = round(
                    float(newBill_row[4]) + float(newBill_row[6]) / float(newBill_row[5]), 2)
                new_stock_addition['quantity'] = newBill_row[5]
                charges = newBill_row[6]
                new_stock_addition['remarks'] = newBill_row[7]
                save_db = newBill_row[8]

                df_row = pd.DataFrame([new_stock_addition])
                listt = list(new_stock_addition.values())
                vals_tuple = [tuple(listt)]
                df_row.columns = CURRENT_HOLDING_DB_HEADER
                # df_row = df_row.drop(columns=['ID', 'User', 'Edit Info', "Mobile Number"])
                set_list = ""
                for k, v in new_stock_addition.items():
                    if k != 'id':
                        set_list = f"{set_list},{k}='{v}'"
                set_list = set_list[1:]

                # print("update val --> ", set_list)
                # https: // stackoverflow.com / questions / 21608228 / conditional - replace - pandas
                # https: // stackoverflow.com / questions / 36909977 / update - row - values - where - certain - condition - is -met - in -pandas / 36910033
                if save_db:
                    # print("updated 2 db")
                    messge = self.total_holdings_details.update_rows_by_column_values(set_argument=set_list,
                                                                                      criteria=f"ref_number='{row_data_db['ref_number']}'")
                    # print(messge)
                    # messge = self.total_holdings_details.insert_row_by_column_values(row_val=vals_tuple)

                mask1 = self.current_holding_data_df["Reference"] == row_data_db['ref_number']
                for k, v in new_stock_addition.items():
                    key = CURRENT_HOLDING_DB_TO_DISPLAY[k]
                    if key in self.current_holding_data_df.columns.values.tolist() and key != 'Reference':
                        self.current_holding_data_df.loc[mask1, key] = new_stock_addition[k]

                self.holdingModel.update(self.current_holding_data_df, key="New")
                self.holdingModel.layoutChanged.emit()
                self.holdingTable.clearSelection()
                # self.calculate_sum()
            else:
                QMessageBox.information(self, 'Insufficient data !!',
                                        f'Insufficient data in selected  transaction/bill..')

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
            row_data_db = self.total_holdings_details.read_row_by_column_values(criteria=search_item)[0]
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
                message = self.total_holdings_details.delete_row_by_column_values(criteria=search_item)
                mask1 = self.current_holding_data_df["Reference"] == int(row_data[0])
                index = self.current_holding_data_df[mask1].index
                self.current_holding_data_df.drop(index, axis=0, inplace=True)
                self.holdingModel.update(self.current_holding_data_df, key="Delete")
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
        new_stock_addition = make_nested_dict()
        row_data = []
        for col in range(ncol):
            val = self.holdingTable.model().index(index, col).data()
            row_data.append(val)

        search_item = f"ref_number = {row_data[0]}"
        row_data_db = self.total_holdings_details.read_row_by_column_values(criteria=search_item)[0]

        # print(row_data)
        print(row_data_db)
        old_price = parse_str(row_data_db['avg_price'])
        old_quantity = parse_str(row_data_db['quantity'])

        if row_data_db['ref_number'] != '':
            sell_stock_inp = sell_selected_stock(row_data_db)
            if sell_stock_inp.exec_() == sell_stock_inp.Accepted:
                newBill_row = sell_stock_inp.get_inp()
                date_time = datetime.strptime(newBill_row[3], DATE_FMT_DMY)
                sold_price = parse_str(newBill_row[4])
                sold_quantity = parse_str(newBill_row[5])
                balance_quantity = old_quantity - sold_quantity
                print("#", date_time)
                print("old_price", old_price)
                print("old_quantity", old_quantity)
                print("sold_price", sold_price)
                print("sold_quantity", sold_quantity)
                if balance_quantity > 0:
                    print("balance_quantity", balance_quantity)
                    set_list = f"quantity = '{balance_quantity}'"
                    search_criteria = f"ref_number = '{row_data_db['ref_number']}'"
                    messge = self.total_holdings_details.update_rows_by_column_values(set_argument=set_list,
                                                                                      criteria=search_criteria)
                    print(messge)

                new_stock_addition['id'] = 0
                new_stock_addition['ref_number'] = str(row_data_db['ref_number'])
                new_stock_addition['agency'] = newBill_row[0]
                new_stock_addition['exchange'] = newBill_row[1]
                new_stock_addition['equity'] = newBill_row[2]
                # new_stock_addition['buy_date'] = dateparser.parse(dateNow)
                date_time = datetime.strptime(newBill_row[3], DATE_FMT_DMY)
                # date_time = datetime.strftime(date_time, DATE_FMT_YMD)
                # datetime = datetime.datetime.strptime(input, format)
                new_stock_addition['buy_date'] = date_time.date()  # newBill_row[3]
                new_stock_addition['avg_price'] = round(
                    float(newBill_row[4]) + float(newBill_row[6]) / float(newBill_row[5]), 2)
                new_stock_addition['quantity'] = newBill_row[5]
                charges = newBill_row[6]
                new_stock_addition['remarks'] = newBill_row[7]

    def stock_avg(self):
        index = self.holdingTable.currentIndex().row()
        ncol = self.holdingModel.columnCount()
        new_stock_addition = make_nested_dict()
        row_data = []
        for col in range(ncol):
            val = self.holdingTable.model().index(index, col).data()
            row_data.append(val)

        # self.overall_holdings
        ref_number = f"ref_number = {row_data[0]}"
        mask = self.overall_holdings['equity'] == "IRCTC"
        print(self.overall_holdings.loc[mask].to_string())
        exit()
        search_item = f"ref_number = {row_data[0]}"
        row_data_db = self.total_holdings_details.read_row_by_column_values(criteria=search_item)[0]
        print(row_data_db)
        print(row_data)
        stock_data = []
        stock_data.clear()
        stock_data.append(row_data_db["exchange"])
        stock_data.append(row_data_db["equity"])
        stock_data.append(row_data_db["buy_date"])
        stock_data.append(row_data_db["avg_price"])
        stock_data.append(row_data_db["quantity"])

        if row_data[0] != "":
            showInfo = average_stocks(stock_data)
            showInfo.exec_()

        # if self.stockList.selectedItems():
        #     agency = self.List_of_agency.currentItem().text()
        #     row_number = self.stockList.currentRow()
        #     invoice = int(self.stockList.item(row_number, 0).text())
        #     one_stock = self.get_stock_info(agency, invoice)
        #
        #     stock_data = []
        #     stock_data.clear()
        #     stock_data.append(one_stock["exchange"])
        #     stock_data.append(one_stock["equity"])
        #     stock_data.append(one_stock["Tdate"])
        #     stock_data.append(one_stock["Tprice"])
        #     stock_data.append(one_stock["quantity"])
        #     stock_data.append(one_stock["Oprice"])
        #
        #     if invoice:
        #         # print(stock_data)
        #         showInfo = average_stocks(stock_data)
        #         showInfo.exec_()
        #     else:
        #         pass

    def clear_and_close(self):
        # print('clear and close')
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
        data = self.total_holdings_details.read_row_by_column_values(criteria=pname_mobile)
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
        # print(df.to_string())
        # print(balance_amount)
        if balance_amount > 0.0:
            self.modify_stock_details(BILL_MODIFY_TYPE[3], balance_amount=balance_amount)
        else:
            QMessageBox.information(self, 'Zero Balance !!',
                                    f'Account of {item_name} has due amount : Rs. {balance_amount}')

    def move_to_unpaid_payin(self):
        # print("Moving to unpaid list")
        # fetch data from mysql
        index = self.holdingTable.currentIndex().row()
        ncol = self.holdingModel.columnCount()
        row_data = []
        for col in range(ncol):
            val = self.holdingTable.model().index(index, col).data()
            row_data.append(val)

        if row_data[1] != '' and row_data[3] != '':
            date_time = datetime.strptime(row_data[1], DATE_FMT_DMY)
            date_time = datetime.strftime(date_time, DATE_FMT_YMD)
            date_time_bill_no = f"date_time = '{date_time}'  and  bill_no = '{row_data[0]}'"
            row_data_db = self.total_holdings_details.read_row_by_column_values(criteria=date_time_bill_no)[0]
            check_id = f"{row_data_db['patient_name']}_{row_data_db['mobile_no']}"
            items0 = [self.Holding_List.item(x).text() for x in range(self.Holding_List.count())]

            if row_data_db['pay_unpaid'] == 0:
                QMessageBox.information(self, 'Incorrect !!',
                                        f'There is no unpaid amount in selected  transaction/bill..')
            elif check_id in items0:
                QMessageBox.information(self, 'Already Registered !!',
                                        f'Selected transaction is already registered')
            else:
                # process data
                # row_data_db = row_data_db[0]
                id = row_data_db['id']
                billNo = row_data_db['bill_no']
                date0 = str(row_data_db['date_time'])
                old_biller = row_data_db['user']
                pname = row_data_db['patient_name']
                mobile_number = 123456789
                headers = self.total_holdings_details.db_header
                name_mobile_inp = get_name_mobile_no(pname)
                if name_mobile_inp.exec_() == name_mobile_inp.Accepted:
                    pnameNew, mobile_number = name_mobile_inp.get_inp()
                    if pnameNew.strip() == "":
                        pnameNew = pname
                    # print(pnameNew, mobile_number)
                    row_data_db['mobile_no'] = mobile_number.strip()
                    row_data_db['patient_name'] = pnameNew.strip()
                    set_list = ""
                    for k, v in row_data_db.items():
                        if k != 'id':
                            set_list = f"{set_list},{k}='{v}'"
                    set_list = set_list[1:]
                    # print(set_list)
                    messge = self.total_holdings_details.update_rows_by_column_values(set_argument=set_list,
                                                                                      criteria=f"id='{id}'")
                    # print(messge)
                    #
                    # print(type(self.df_reception_payin))
                    # print(self.df_reception_payin.columns)

                    mask1 = self.df_reception_payin["Bill Number"] == billNo
                    mask2 = self.df_reception_payin["Date"] == date0
                    index = self.df_reception_payin[mask1 & mask2].index
                    # self.df_reception_payin.drop(index, axis=0, inplace=True)
                    # print(index)
                    # print(self.df_reception_payin.iloc[index])
                    self.df_reception_payin.loc[index, ["Patient Name"]] = pnameNew
                    self.holdingModel.update(self.df_reception_payin, key="New")
                    self.holdingModel.layoutChanged.emit()
                    self.holdingTable.clearSelection()
                    id = f"{pnameNew}_{mobile_number}"

                    items = [self.Holding_List.item(x).text() for x in range(self.Holding_List.count())]
                    if id not in items:
                        self.Holding_List.addItem(id)
        else:
            QMessageBox.information(self, 'Insufficient data !!',
                                    f'Insufficient data in selected  transaction/bill..')


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    gui_switch = return_history_range_selection(True)
    gui_switch.show()
    # if gui_switch.exec_() == gui_switch.Accepted:
    #     plot_all_data = gui_switch.get_inp()
    #     print("Plot all data ?",plot_all_data)

    sys.exit(app.exec_())