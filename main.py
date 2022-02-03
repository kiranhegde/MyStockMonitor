import datetime
from pathlib import Path

import pandas as pd
from PyQt5.QtCore import Qt, QTimer, QCoreApplication, QProcess
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QAction, QFileDialog, QTabWidget \
    , QMainWindow, QApplication, QMenu

# import PyQt5.sip # required to function exe file
import PyQt5.sip

from utility.libnames import WELCOME
from mysql_tools.mysql_crud import mysql_table_crud

# PEP8 Reformat Code press Ctrl+Alt+L.


class MyMainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.welcome = WELCOME
        self.setWindowTitle(self.welcome)
        self.setWindowIcon(QIcon('icons/ksirtet.ico'))
        self.setGeometry(450, 150, 750, 600)
        self.statusBar()
        self.close_now = False
        self.UI()
        # self.setWindowState(Qt.WindowMaximized)
        # self.showNormal()
        # self.showMaximized()
        # self.showFullScreen()

    def UI(self):
        # self.check_sqlite_db_info()
        # self.extablish_db_connection()
        # self.check_db_tables_exists()
        # self.get_parameter_values()

        # backup_mysql(**self.db_cfg)
        # exit()
        # self.add_columns_name_to_table()
        # self.my_login()
        # print(self.user_list)
        self.toolBarMenu()
        self.toolBar()
        # self.tabWidgets()
        # self.get_column_value_count()
        # self.widgets()

    # @mysql_db(DB_CFG)
    # def check_mysql(self):
    #     pass
    def get_parameter_values(self):

        parameter_conn = mysql_table_crud(db_table=PARAMETER_VALUES,
                                          db_header=PARAMETER_VALUES_HEADER,
                                          **self.db_cfg)

        para = parameter_conn.read_row_by_column_values(column_name="*")
        para_df = pd.DataFrame(para)

        if len(para_df) == 0:
            # https: // blog.softhints.com / insert - multiple - rows - at - once -with-python - and -mysql /
            initial_values = [(0, 'medical_gui', 1),
                              (0, 'hospital_gui', 0)
                              ]
            messge = parameter_conn.insert_row_by_column_values(row_val=initial_values)
            para = parameter_conn.read_row_by_column_values(column_name="*")
            para_df = pd.DataFrame(para)

        para_df.drop(['id'], axis=1, inplace=True)
        mask1 = para_df['parameter_name'] == 'medical_gui'
        mask2 = para_df['parameter_name'] == 'hospital_gui'
        self.bsheet_medical = bool(para_df.loc[mask1, ['check_condition']].values[0][0])
        self.bsheet_hospital = bool(para_df.loc[mask2, ['check_condition']].values[0][0])

    def update_window_title(self, usr):
        if self.bsheet_medical:
            self.welcome = "Durga Medicals, Daily Transaction"
            self.setWindowTitle(f"{self.welcome} ( {usr} )")
        else:
            self.setWindowTitle(f"{self.welcome} ( {usr} )")

    def widgets(self):
        self.bsheet_selected = make_nested_dict()
        # self.bsheet_loaded = []
        self.bsheet_displayed = make_nested_dict()

        self.print_message = "Welcome"
        # self.bsheet_title="0"
        # self.bsheet_count=0
        self.BSheet_Today()

    def get_column_value_count(self):
        payin_table = mysql_table_crud(db_table=HOSPITAL_BILL_PAYIN_PREFIX,
                                       db_header=PAYIN_TABLE_HEADER,
                                       **self.db_cfg)
        table_list = payin_table.get_column_value_count("department")
        dpt = [list(item.values())[0] for item in table_list]
        # print(dpt)
        dept = make_nested_dict()
        for item in table_list:
            # print(list(item.values())[0],list(item.values())[1])
            dept[list(item.values())[0]] = list(item.values())[1]

        # print(dept)

    def check_sqlite_db_info(self):
        sqlite_db_path = f"Database/{MYSQL_SQLITE_DB}"
        file_path = Path(sqlite_db_path)

        try:
            my_abs_path = file_path.resolve(strict=True)
        except FileNotFoundError:
            # # logger.critical("Failed to connect to MYSQL server")
            # msg = TimerMessageBox(10, "Database file missing !!",
            #                       f"{sqlite_db_path} missing ...\nExiting... ")
            # msg.exec_()
            # self.quit_now()

            mbox0 = QMessageBox.question(self, "MySQL database login issue!",
                                         "MYSQL login information table missing \nCreate new sql database ? ",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            message = ""
            if mbox0 == QMessageBox.Yes:
                self.mysql_hostname = "localhost"
                self.mysql_login = "kiran"
                self.mysql_passwd = "mypassword"
                self.mysql_dbname = "rk_hospital_new"
                self.mysql_port = "3306"
                # logger.warning(f"{self.mysql_dbname} MYSQL DB created ")
                # message = mysql_table_crud(**cfg_db).create_database(dbname=self.mysql_dbname)
                db = sqlite3_crud(filename=file_path, table=MYSQL_SQLITE_DB_LOGIN)
                sql = db.mysql_login(MYSQL_SQLITE_DB_LOGIN)
                db.sql_do(sql)
                message = f"{file_path} created with table {MYSQL_SQLITE_DB_LOGIN}"
                QMessageBox.information(self, "Database creation", message)
            else:
                # logger.warning(f"{self.mysql_dbname}  MYSQL DB required ")
                QMessageBox.question(self, "Exiting !", "Provide sql database with login information...  ",
                                     QMessageBox.Ok, QMessageBox.Ok)
                self.quit_now()
        else:
            pass
            # logger.info("Connected to MYSQL server")

        # self.mysql_log_data = sqlite3_crud(filename=f"{my_abs_path}", table=MYSQL_SQLITE_DB_LOGIN)
        # print(self.mysql_log_data.mysql_login())

    def extablish_db_connection(self):
        # logger.info("Connecting to MYSQL server")
        sqlite_db_path = f"Database/{MYSQL_SQLITE_DB}"
        file_path = Path(sqlite_db_path)
        # print('extablish_db_connection')

        try:
            my_abs_path = file_path.resolve(strict=True)
        except FileNotFoundError:
            # logger.critical("Failed to connect to MYSQL server")
            msg = TimerMessageBox(10, "Database file missing !!",
                                  f"{sqlite_db_path} missing ... \n {self.print_message} \nExiting... ")
            msg.exec_()
            self.quit_now()
        else:
            pass
            # logger.info("Connected to MYSQL server")

        self.mysql_log_data = sqlite3_crud(filename=f"{my_abs_path}", table=MYSQL_SQLITE_DB_LOGIN)
        table_empty = self.mysql_log_data.check_table_empty(MYSQL_SQLITE_DB_LOGIN)

        if table_empty == 0:
            mbox0 = QMessageBox.question(self, "MYSQL login issue !! ",
                                         "MYSQL login table empty ... \n Would you like to provide update login ? ",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if mbox0 == QMessageBox.Yes:
                self.mysql_hostname = "localhost"
                self.mysql_login = "kiran"
                self.mysql_passwd = "mypassword"
                self.mysql_dbname = "rk_hospital_new"
                self.mysql_port = "3306"
                # logger.info("Getting MYSQL server info")
                self.mysql_login_info(close_now=self.close_now)
                self.quit_now()
            else:
                # logger.warning(f"{self.mysql_dbname}  MYSQL DB required ")
                QMessageBox.question(self, "Exiting !",
                                     "MYSQL login table empty...\nCannot login to server without credentials  ",
                                     QMessageBox.Ok, QMessageBox.Ok)
                self.quit_now()

        else:
            mysql_log = self.mysql_log_data.retrieve('1')
            self.mysql_hostname = mysql_log['mysql_hostname']
            self.mysql_login = mysql_log['mysql_login']
            self.mysql_passwd = mysql_log['mysql_passwd']
            self.mysql_dbname = mysql_log['mysql_dbname']
            self.mysql_port = mysql_log['mysql_port']

            self.db_cfg = dict(user=mysql_log['mysql_login'],
                               passwd=mysql_log['mysql_passwd'],
                               port=mysql_log['mysql_port'],
                               host=mysql_log['mysql_hostname'],
                               db=mysql_log['mysql_dbname'])

            cfg_db = dict(user=mysql_log['mysql_login'],
                          passwd=mysql_log['mysql_passwd'],
                          port=mysql_log['mysql_port'],
                          host=mysql_log['mysql_hostname'])

            db_check, self.print_message = mysql_table_crud(**cfg_db).check_db_exists(self.mysql_dbname)

            if not db_check:
                # logger.warning("MYSQL DB missing..")
                mbox0 = QMessageBox.question(self, "Database Missing !", "Create new database ? ",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                if mbox0 == QMessageBox.Yes:
                    # logger.warning(f"{self.mysql_dbname} MYSQL DB created ")
                    message = mysql_table_crud(**cfg_db).create_database(dbname=self.mysql_dbname)
                    QMessageBox.information(self, "Database creation", message)
                else:
                    # logger.warning(f"{self.mysql_dbname}  MYSQL DB required ")
                    QMessageBox.question(self, "Exiting !", "Provide Database connection and try again...  ",
                                         QMessageBox.Ok, QMessageBox.Ok)
                    self.quit_now()

            connection, self.print_message = mysql_table_crud(**self.db_cfg).db_connection()
            if not connection:
                # logger.critical("Access denied !!  MYSQL server connection failed")
                mbox0 = QMessageBox.question(self, "Access denied !! ",
                                             "Failed to connect to server ... \n Would you like to provide updated login ? ",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if mbox0 == QMessageBox.Yes:
                    # logger.info("Getting MYSQL server info")
                    self.mysql_login_info(close_now=self.close_now)
                    self.quit_now()
                else:
                    # logger.critical("exiting !!  MYSQL server connection failed")
                    msg = TimerMessageBox(10, "Access denied !!",
                                          f"Failed to connect to server ... \n {self.print_message} \nExiting... ")
                    msg.exec_()
                    self.quit_now()

    def check_db_tables_exists(self):

        list_of_tables = {
            # "xyz": create_receptionPAYIN_table_db_query("xyz"),
            PHARAMACY_BILL_PAYIN_PREFIX: create_pharmacyPAYIN_table_db_query(PHARAMACY_BILL_PAYIN_PREFIX),
            PHARAMACY_BILL_PAYOUT_PREFIX: create_pharmacyPAYOUT_table_db_query(PHARAMACY_BILL_PAYOUT_PREFIX),
            HOSPITAL_BILL_PAYIN_PREFIX: create_receptionPAYIN_table_db_query(HOSPITAL_BILL_PAYIN_PREFIX),
            HOSPITAL_BILL_PAYOUT_PREFIX: create_receptionPAYOUT_table_db_query(HOSPITAL_BILL_PAYOUT_PREFIX),
            MYSQL_DB_HOSPITAL_DEPT_PAYIN: create_payin_department_list_table(MYSQL_DB_HOSPITAL_DEPT_PAYIN),
            MYSQL_DB_HOSPITAL_DETAIL_PAYOUT: create_payout_detail_list_table(MYSQL_DB_HOSPITAL_DETAIL_PAYOUT),
            MYSQL_DB_PHARAMACY_DEPT_PAYIN: create_payin_department_list_table(MYSQL_DB_PHARAMACY_DEPT_PAYIN),
            MYSQL_DB_PHARAMACY_DETAIL_PAYOUT: create_payout_detail_list_table(MYSQL_DB_PHARAMACY_DETAIL_PAYOUT),
            LOGIN_TABLE: create_user_login_table(LOGIN_TABLE),
            UNPAID_LIST: create_unpaid_detail_list_table(UNPAID_LIST),
            PARAMETER_VALUES: check_parameter_conditions(PARAMETER_VALUES)
        }

        for table in list_of_tables.keys():
            table_list, print_message = mysql_table_crud(db_table=table, **self.db_cfg).check_table_exists()
            # table_list = [item[0] for item in table_list]
            table_list = [list(item.values())[0] for item in table_list]

            if table not in table_list:
                mbox0 = QMessageBox.question(self, "Create Database",
                                             f"Database empty \nCreate  database  table {table}  ? ",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

                if mbox0 == QMessageBox.Yes:
                    query = list_of_tables[table]
                    print_message = mysql_table_crud(**self.db_cfg).create_table(query)
                    QMessageBox.information(self, "Table creation", print_message)

    def add_columns_name_to_table(self):
        payin_table = mysql_table_crud(db_table=HOSPITAL_BILL_PAYIN_PREFIX,
                                       db_header=PAYIN_TABLE_HEADER,
                                       **self.db_cfg)
        payout_table = mysql_table_crud(db_table=HOSPITAL_BILL_PAYOUT_PREFIX,
                                        db_header=PAYOUT_TABLE_HEADER,
                                        **self.db_cfg)

        message = payin_table.add_column_name_to_table("mobile_no", 'BIGINT')
        print(message)
        message = payout_table.add_column_name_to_table("mobile_no", 'BIGINT')
        print(message)
        exit()

    def my_login(self):
        # logger.warning("Trying login")
        self.user_list = self.get_user_list()
        rk_db, self.print_message = mysql_table_crud(**self.db_cfg).db_connection()
        if self.bsheet_medical:
            title = "Durga Medicals"
        else:
            title = "RK Hospital"

        login = Login(rk_db, title)
        if login.exec_() == login.Accepted:
            self.usr, self.pwd, self.my_access, self.tools = login.get_inp()

            if self.bsheet_medical:
                if self.tools == LOGIN_TOOL[0] or self.tools == LOGIN_TOOL[2]:
                    self.update_window_title(self.usr)
                else:
                    QMessageBox.warning(self, 'Incorrect login (Medical) !!',
                                        'Please check User name,  password, tool access...')
                    self.quit_now()

            if self.bsheet_hospital:
                if self.tools == LOGIN_TOOL[1] or self.tools == LOGIN_TOOL[2]:
                    self.update_window_title(self.usr)
                else:
                    QMessageBox.warning(self, 'Incorrect login (Hospital) !!',
                                        'Please check User name,  password, Tool access...')
                    self.quit_now()

        else:
            # logger.warning("Quitting the program")
            # QMessageBox.critical(self, 'Login  !!', 'Login required \n Exiting....                   ')
            self.quit_now()

    def BSheet_Today(self):
        # checking PAYIN table
        # logger.info(f"Today's bsheet opened")
        self.usr_show = self.usr
        self.by_user = False
        # self.usr_show="All"
        self.deptmt = "All"
        self.payDetail = "All"
        self.receiptPayMethod = "All"
        self.search_options = ["All", "All", "All", "All"]

        bill_date = datetime.datetime.now()
        # print(bill_date, type(bill_date))
        start_time, end_time = date_time_day_start_end(bill_date)
        start_time = start_time.strftime("%Y-%m-%d, %H:%M:%S")
        end_time = end_time.strftime("%Y-%m-%d, %H:%M:%S")

        # print("2", start_time, end_time)
        title = f"Today: {datetime.date.today()}"

        self.bsheet_selected[title] = [start_time, end_time]
        # self.bsheet_displayed[bill_date] = [start_time, end_time]
        # print(start_time, end_time)
        # print(self.bsheet_selected)
        # print(self.bsheet_displayed)

        self.load_selected_bsheets()

    def load_casesheet_detail(self):
        # print("not implemented")
        title = "Unpaid Accounts"
        if title not in self.bsheet_displayed.keys():
            self.bsheet_displayed[title] = "CaseSheet"
            if self.bsheet_hospital:
                self.tabs.addTab(list_of_casesheet_with_details_hospital(self.usr_show, self.my_access, **self.db_cfg),
                                 title)
            if self.bsheet_medical:
                self.tabs.addTab(list_of_casesheet_with_details_medical(self.usr_show, self.my_access, **self.db_cfg),
                                 title)

            Curr_index = [index for index in range(self.tabs.count()) if title == self.tabs.tabText(index)]
            self.tabs.setCurrentIndex(Curr_index[0])

    def load_by_date_time(self):
        self.usr_show = ""
        self.by_user = True
        # print(self.user_list)
        # print("Displayed:",self.bsheet_displayed)
        bsheet_inp = select_bsheet(self.bsheet_displayed.keys(), self.usr, self.user_list)
        self.bsheet_selected.clear()
        if bsheet_inp.exec_() == bsheet_inp.Accepted:
            start_time, end_time, self.usr_show, self.deptmt, self.receiptPayMethod, self.payDetail, self.search_options = bsheet_inp.get_inp()
            title = BSHEET_TITLE
            # if self.usr_show == self.usr:
            #     pass
            # else:
            if self.deptmt == "All":
                title = f" {title} ({self.usr_show})"
            else:
                title = f" {title}_{self.deptmt}({self.usr_show})"
            # print(title)
            # print("}}}}}",start_time, end_time)
            # if [start_time, end_time] not in  self.bsheet_displayed.values():
            if title not in self.bsheet_displayed.keys():
                # self.bsheet_count=self.bsheet_count+1
                # title=BSHEET_TITLE #+str(self.bsheet_count)

                # https: // stackoverflow.com / questions / 373370 / how - do - i - get - the - utc - time - of - midnight -for -a - given - timezone
                # start_time=datetime.datetime.strptime(start_time,"%d-%m-%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                # end_time=datetime.datetime.strptime(end_time,"%d-%m-%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                self.bsheet_selected[title] = [start_time, end_time]
                # print("--->", self.bsheet_selected)
                self.load_selected_bsheets(check=False)

    def load_selected_bsheets(self, check=True):
        if len(self.bsheet_selected.keys()) != 0:
            for title in self.bsheet_selected.keys():
                # print("Loading",table,self.tabs.currentIndex())
                # print("selected:",self.bsheet_selected)
                # if table not in self.bsheet_loaded:
                if title not in self.bsheet_displayed.keys():
                    start_end_time = self.bsheet_selected[title]
                    self.bsheet_displayed[title] = [start_end_time[0], start_end_time[1]]
                    # mysql_data = []
                    # mysql_data.append(self.mysql_login)
                    # mysql_data.append(self.mysql_passwd)
                    # mysql_data.append(self.mysql_dbname)
                    # mysql_data.append(self.mysql_hostname)
                    # mysql_data.append(self.mysql_port)
                    if self.bsheet_medical:
                        self.tabs.addTab(
                            PharmacyBsheet(self.usr_show, start_end_time, check, self.search_options, **self.db_cfg),
                            title)
                    else:
                        self.tabs.addTab(
                            HospitalBsheet(self.usr_show, start_end_time, check, self.search_options, **self.db_cfg),
                            title)

                    Curr_index = [index for index in range(self.tabs.count()) if title == self.tabs.tabText(index)]
                    self.tabs.setCurrentIndex(Curr_index[0])
                else:
                    QMessageBox.information(self, "Already displayed",
                                            f"{title} already loaded,\n please close the existing and try again ")
            #

        else:
            print("No balance sheet selected..")
            self.quit_now()

        self.bsheet_selected.clear()

    def toolBarMenu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")
        # filecmp_menu = menubar.addMenu("&File")

        # menubar.setLayoutDirection(Qt.RightToLeft)
        setting_menu = menubar.addMenu("Settings")
        # if self.my_access != "Administrator":
        #     setting_menu.setEnabled(False)
        # setting_menu=menubar.addMenu(QIcon("icons/configure-2.png"),"Settings")

        user_admin_submenu = QMenu("&User Administration", self)
        add_user_menu = QAction("&New user", self)
        add_user_menu.triggered.connect(self.user_admin)
        add_user_menu.setStatusTip('Add new user')
        user_admin_submenu.addAction(add_user_menu)

        edit_user_menu = QAction("Modify user", self)
        edit_user_menu.setStatusTip('Modify user credential ')
        user_admin_submenu.addAction(edit_user_menu)

        setting_menu.addMenu(user_admin_submenu)
        # --------------------------------------
        deptmt_submenu = QMenu("&Department (Receipt)", self)
        add_deptmt_menu = QAction("&Modify Department", self)
        add_deptmt_menu.triggered.connect(self.department_modify_setting)
        add_deptmt_menu.setStatusTip('Modify list of Departments in receipt')
        deptmt_submenu.addAction(add_deptmt_menu)

        edit_deptmt_menu = QAction("Display Department", self)
        edit_deptmt_menu.setStatusTip('Select list of Departments to be displayed')
        deptmt_submenu.addAction(edit_deptmt_menu)

        setting_menu.addMenu(deptmt_submenu)
        # --------------------------------------

        detail_submenu = QMenu("&Details (Payment)", self)
        add_detail_menu = QAction("&Modify Details", self)
        add_detail_menu.setStatusTip('Modify list of Details in payment')
        detail_submenu.addAction(add_detail_menu)

        edit_detail_menu = QAction("Display Details", self)
        edit_detail_menu.setStatusTip('Select list of Details to be displayed')
        detail_submenu.addAction(edit_detail_menu)

        setting_menu.addMenu(detail_submenu)
        # --------------------------------------
        mysql_submenu = QMenu("&MYSQL", self)
        mysql_login = QAction("&Login Credential", self)
        mysql_login.triggered.connect(self.mysql_login_info0)
        mysql_login.setStatusTip('Modify MYSQL Login Info.')
        mysql_submenu.addAction(mysql_login)

        setting_menu.addMenu(mysql_submenu)
        # --------------------------------------
        # switch_submenu = QMenu("&Medical/Hospital Switch", self)
        # gui_switch = QAction("&Medical or Hospital", self)
        # gui_switch.triggered.connect(self.gui_switching)
        # gui_switch.setStatusTip('Switch Hospital between Medical software')
        # switch_submenu.addAction(gui_switch)
        #
        # setting_menu.addMenu(switch_submenu)

    def toolBar(self):

        tb = self.addToolBar("Tool Bar")
        tb.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        tb.addSeparator()
        BSheet_today = QAction(QIcon("icons/db_add.png"), "Today", self)
        BSheet_today.triggered.connect(self.BSheet_Today)
        BSheet_today.setStatusTip("Today's information/data")
        BSheet_today.setToolTip("Today's information/data")
        tb.addAction(BSheet_today)
        tb.addSeparator()

        # delShare = QAction(QIcon("icons/db_remove.png"), "Delete \n ", self)
        # # delShare.triggered.connect(self.del_shareDB)
        # delShare.setStatusTip("Removing items from database")
        # delShare.setToolTip("Removing items from database")
        # tb.addAction(delShare)
        # tb.addSeparator()

        load_sheet = QAction(QIcon("icons/docu.png"), "Load ", self)
        load_sheet.triggered.connect(self.load_by_date_time)
        load_sheet.setStatusTip("Load Old Balance Sheet")
        load_sheet.setToolTip("Load Old Balance Sheet ")
        tb.addAction(load_sheet)
        tb.addSeparator()

        load_casesheet = QAction(QIcon("icons/document_open1.png"), "Unpaid A/C", self)
        load_casesheet.triggered.connect(self.load_casesheet_detail)
        load_casesheet.setStatusTip("Individual Balance Sheet")
        load_casesheet.setToolTip("Individual Balance Sheet ")
        tb.addAction(load_casesheet)
        tb.addSeparator()

        statement_file = QAction(QIcon("icons/document-print.png"), "Statement", self)
        statement_file.triggered.connect(self.report_to_excel)
        statement_file.setStatusTip("Statement(Excel file) for the given time range")
        statement_file.setToolTip("Statement(Excel file) for the given time range")
        tb.addAction(statement_file)
        tb.addSeparator()
        # if self.my_access == "Write Only":
        #     statement_file.setEnabled(False)

        import_data = QAction(QIcon("icons/document-import.png"), "Import", self)
        import_data.triggered.connect(self.call_import_csv_to_mysql)
        import_data.setStatusTip("Import data from CSV")
        import_data.setToolTip("Import data from CSV")
        tb.addAction(import_data)
        tb.addSeparator()
        # if self.my_access != "Administrator":
        #     import_data.setEnabled(False)

        export_data = QAction(QIcon("icons/document-export.png"), "Export", self)
        export_data.triggered.connect(self.export_mysql_csv)
        export_data.setStatusTip("Export data from CSV")
        export_data.setToolTip("Export data from CSV")
        tb.addAction(export_data)
        tb.addSeparator()
        # if self.my_access != "Administrator":
        #     export_data.setEnabled(False)

        # settings_default = QAction(QIcon("icons/configure-2.png"), "Settings", self)
        # settings_default.triggered.connect(self.all_setting)
        # settings_default.setStatusTip("default parameter settings")
        # settings_default.setToolTip("default parameter settings")
        # tb.addAction(settings_default)
        # tb.addSeparator()
        # if self.my_access != "Administrator":
        #     settings_default.setEnabled(False)

        # user_admin = QAction(QIcon("icons/user-new.png"), "User\nAdmin", self)
        # user_admin.triggered.connect(self.user_admin)
        # user_admin.setStatusTip("default parameter settings")
        # user_admin.setToolTip("default parameter settings")
        # tb.addAction(user_admin)
        # tb.addSeparator()
        # if self.my_access != "Administrator":
        #     user_admin.setEnabled(False)

        # refreshShare = QAction(QIcon("icons/view-refresh-6.png"), "Refresh", self)
        # refreshShare.triggered.connect(self.refresh)
        # refreshShare.setStatusTip("loading latest  from database")
        # refreshShare.setToolTip("loading latest  from database")
        # tb.addAction(refreshShare)
        # tb.addSeparator()
        # if self.my_access != "Administrator":
        #     refreshShare.setEnabled(False)

        restartShare = QAction(QIcon("icons/quick_restart.png"), "Restart", self)
        restartShare.triggered.connect(self.restart)
        restartShare.setStatusTip("loading latest  settings")
        restartShare.setToolTip("loading latest settings")
        tb.addAction(restartShare)
        tb.addSeparator()
        # if self.my_access != "Administrator":
        #     refreshShare.setEnabled(False)

        # refreshShare = QAction(QIcon("icons/view-refresh-6.png"), "Log", self)
        # refreshShare.triggered.connect(self.refresh)
        # refreshShare.setStatusTip("loading latest  from database")
        # refreshShare.setToolTip("loading latest  from database")
        # tb.addAction(refreshShare)
        # tb.addSeparator()

        quit_app = QAction(QIcon("icons/quit.png"), "Quit", self)
        quit_app.triggered.connect(self.quit_now)
        quit_app.setStatusTip("Closing the application")
        quit_app.setToolTip("Closing the application")
        tb.addAction(quit_app)
        tb.addSeparator()

    def user_admin(self):
        pass

    def mysql_login_info0(self):
        pass

    def department_modify_setting(self):
        pass

    def restart(self):
        QCoreApplication.quit()
        status = QProcess.startDetached(sys.executable, sys.argv)
        # print(status)

    def refresh(self):
        pass


    def quit_now(self):
        # logger.info(f"Exiting the program..")
        sys.exit(0)

    def export_mysql_csv(self):
        # rk_db = mysql_table_crud.db_connection()
        rk_db, print_message = mysql_table_crud(**self.db_cfg).db_connection()
        # logger.info(f"Exporting data to CSV by {self.usr}")
        export_inp = export_mysql_dates(rk_db)
        if export_inp.exec_() == export_inp.Accepted:
            message = export_inp.get_inp()
            # logger.info(f"Exported to CSV file..")
        else:
            pass
            # #logger.info(f"Export to CSV cancelled")

    def call_import_csv_to_mysql(self):

        # import_csv = import_csv_to_mysql(MSQL_LOGIN,MSQL_PASSWD,)
        # logger.info(f"CSV file imported by {self.usr}")
        from sqlalchemy import create_engine
        # sqlEngine = create_engine('mysql+pymysql://kiran:@localhost/rk_hospital', pool_recycle=3600)
        query = f"mysql+mysqldb://{self.mysql_login}:{self.mysql_passwd}@{self.mysql_hostname}/{self.mysql_dbname}"
        # sqlEngine = create_engine("mysql+mysqldb://kiran:pass1word@localhost/rk_hospital")  # fill details
        sqlEngine = create_engine(query)
        dbConnection = sqlEngine.connect()

        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileName, result = QFileDialog.getOpenFileName(self, "QFileDialog.getSaveFileName()", "", "(*.csv)",
                                                       options=options)

        # print("fname",fileName,result)
        if fileName:
            # logger.info(f"Reading  CSV  file {fileName}  by {self.usr}")
            csv_data = pd.read_csv(fileName)
            # print(csv_data.to_string())
            csv_data.to_sql(name='reception_statement_payin_test1', con=dbConnection, index=False, if_exists='append',
                            index_label='id')
            return
        else:
            return

    def report_to_excel(self):
        # user_list=[]
        # user_list.clear()
        # print("0", self.user_list)
        # logger.info(f"Excel report generation: {self.usr}")
        # rk_db = mysql_table_crud.db_connection()

        rk_db, print_message = mysql_table_crud(**self.db_cfg).db_connection()
        if self.bsheet_medical:
            export_inp = report_to_excel_by_date(rk_db, self.usr, self.user_list, pharmacy=True)
        else:
            export_inp = report_to_excel_by_date(rk_db, self.usr, self.user_list)
        if export_inp.exec_() == export_inp.Accepted:
            message = export_inp.get_inp()
            # logger.info(f"Excel report generated  by {self.usr}")
        else:
            pass

    # export_inp = export_mysql_dates(self.rk_db)
    # if export_inp.exec_() == export_inp.Accepted:
    #     message = export_inp.get_inp()
    # else:
    #     pass

    def get_user_list(self):
        login_conn = mysql_table_crud(db_table=LOGIN_TABLE,
                                      db_header=USER_LOGIN_TABLE_HEADER,
                                      **self.db_cfg)

        user_list = login_conn.read_row_by_column_values(column_name="user_name", order="order by user_name asc")
        # print(user_list)
        # login_list = [item[0] for item in user_list]
        login_list = [list(item.values())[0] for item in user_list]
        # print(login_list)

        if len(login_list) == 0:
            # logger.info(f"Login database empty..")
            mbox0 = QMessageBox.question(self, "Login Database missing..",
                                         "Login is required to continue...\n Register new users for login ?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if mbox0 == QMessageBox.Yes:
                self.user_admin()
                user_list = login_conn.read_row_by_column_values(column_name="user_name",
                                                                 order="order by user_name asc")
                login_list = [item[0] for item in user_list]
            else:
                msg = TimerMessageBox(4, "Quiting...", "Login is required to continue...\n Register users for login")
                msg.exec_()
                self.quit_now()

        user_list = []
        user_list = USER_LIST
        for name in login_list:
            user_list.append(name)
        return user_list

    # def read_mysql(self):
    #     df_all = pd.read_sql(SQL_READ_RECPT_BILL, con=self.rk_db)
    #     df_all.columns = HEADER_RECPT_DEBIT
    #     df_display=df_all.drop(columns=['User','Edit Info'])
    #     # print(len(df_display))
    #     self.bill_count=len(df_display)
    #
    #     return df_display

    def tabWidgets(self):
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.tab_close)
        self.tabs.setFont(FONT1)
        self.setCentralWidget(self.tabs)

    # def refresh(self):
    #     self.LoadAll()
    #     # self.listAgency, self.stockDB = self.read_all_stocks()
    #     # self.List_of_agency=self.get_agency_list(self.listAgency)

    def tab_close(self, index):

        # https: // stackoverflow.com / questions / 63122385 / pyqt5 - tab - widget - how - can - i - get - the - index - of - active - tab - window - on - mouse - click
        # https: // stackoverflow.com / questions / 19151159 / qtabwidget - close - tab - button - not -working
        # self.tabs.tabCloseRequested.connect(lambda index: tabs.removeTab(index))
        tabname = self.tabs.tabText(index)
        # logger.info(f"{tabname} closed  by {self.usr}")
        self.bsheet_displayed.pop(tabname)
        # print("Loaded Tab:",self.bsheet_displayed)
        # print("Selected Tab:",self.bsheet_selected)
        self.tabs.removeTab(index)


def main():
    app = QApplication(sys.argv)
    window = MyMainWindow()
    # import resource
    # print( resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    window.showMaximized()
    sys.exit(app.exec_())


# def exception_hook(exctype, value, traceback):
#     from Logging.my_logger import setup_log, clearlogger
#     import traceback
#
#     logger = setup_log()
#     sys._excepthook = sys.excepthook
#     # print(exctype, value, traceback)
#     logger.error("An uncaught exception occurred:")
#     logger.error("Type: %s", exctype)
#     logger.error("Value: %s", value)
#     logger.error("Value: %s", traceback)
#
#     if traceback:
#         format_exception = traceback.format_tb(traceback)
#         for line in format_exception:
#             logger.error(repr(line))
#
#     sys.exit(1)

def custom_excepthook(exc_type, exc_value, exc_traceback):
    # https: // stackoverflow.com / questions / 6234405 / logging - uncaught - exceptions - in -python
    from Logging.my_logger import setup_log, clearlogger
    import traceback

    logging = setup_log()
    # Do not print exception when user cancels the program
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("An uncaught exception occurred:")
    logging.error(f"Type: {exc_type}")
    logging.error(f"Value: {exc_value}")

    if exc_traceback:
        format_exception = traceback.format_tb(exc_traceback)
        logging.error(f"\n{format_exception[0]}")
        # for line in format_exception:
        #     print(line[0])
        # logging.error(repr(line))

    sys.exit(1)


# def except_hook(cls, exception, traceback):
#     sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    import sys

    # import traceback
    # import logging
    # from Logging import config

    # from Logging.my_logger import get_logger ,clear_logger

    # #logger = logging.get#logger(__name__)
    # #logger.info()
    # import cProfile
    # import pstats
    # pr = cProfile.Profile()
    # pr.enable()

    # sys.excepthook = except_hook
    # sys.excepthook = exception_hook

    # ======================================
    # log file for the tool
    sys.excepthook = custom_excepthook
    # try:
    main()
    # ======================================

    # except Exception as err:
    # from Logging.my_logger import setup_log, clearlogger
    # import traceback

    # sys.excepthook = exception_hook
    # logger = setup_log()
    # logger.error("Error ")
    # logger.error(err)
    # logger.error(traceback.format_exc())

    # pr.disable()
    # pr.dump_stats('profiler_output.txt')
    # profiler_stats = pstats.Stats("profiler_output.txt")
    # profiler_stats.sort_stats('cumulative').print_stats(20)

    # f = open('profile.txt', 'a')
    #
    # sortby = 'cumulative'
    # pstats.Stats(pr, stream=f).strip_dirs().sort_stats(sortby).print_stats()

    # f.close()
