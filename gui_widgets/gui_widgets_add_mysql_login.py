from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QIcon, QRegExpValidator
from PyQt5.QtWidgets import QDialog, QLineEdit, QLabel, QPushButton, QFormLayout

from utility.utility_functions import make_nested_dict


class update_mysql_login(QDialog):
    def __init__(self, MYSQL_HOST_NAME, DBNAME, MYSQL_LOGIN, MYSQL_PASSWD, MYSQL_PORT, parent=None):
        super(update_mysql_login, self).__init__(parent)
        self.setWindowTitle('MYSQL Login Details')
        self.setWindowIcon(QIcon('icons/new_user.png'))
        self.resize(300, 150)

        self.login = MYSQL_LOGIN
        self.pwd = MYSQL_PASSWD
        self.hname = MYSQL_HOST_NAME
        self.db_name = DBNAME
        self.port_number = MYSQL_PORT

        self.userName = QLineEdit(self)
        # regex1 = QRegExp("[a-z0-9]")
        # regex = "^[A-Za-z]\\w{5, 29}$"
        # unameValidate = QRegExpValidator(QRegExp(USERNAME_REGEX), self.userName)
        # self.userName.setValidator(unameValidate)
        regx = QRegExp(r'^[a-zA-Z0-9_.-]+$')
        # regx=QRegExp("^(?!_$)(?![-.])(?!.*[_.-]{2})[a-zA-Z0-9_.-]+(?<![.-])$")
        unameValidate = QRegExpValidator(regx, self.userName)
        self.userName.setValidator(unameValidate)
        self.userName.setPlaceholderText('Please enter mysql login name')
        self.userName.setPlaceholderText(self.login)
        self.UserLabel = QLabel('<font size="3"> User Name </font>')

        self.passWord = QLineEdit(self)
        self.passWord.setPlaceholderText('Please type mysql  password')
        self.passWord.setPlaceholderText(self.pwd)
        self.PasswordLabel = QLabel('<font size="3"> Password </font>')
        self.passWord.setEchoMode(QLineEdit.Password)

        # self.passWord1 = QLineEdit(self)
        # self.passWord1.setPlaceholderText('Please retype mysql your password')
        # self.PasswordLabel1 = QLabel('<font size="3"> Password (retype) </font>')
        # self.passWord1.setEchoMode(QLineEdit.Password)

        self.hostname = QLineEdit()
        self.hostname.setText(self.hname)
        self.hostnameLabel = QLabel('<font size="3"> Hostname: </font>')
        # self.hostname.addItems(LOGIN_ACCESS)

        self.dbname = QLineEdit()
        self.dbname.setText(self.db_name)
        self.dbnameLabel = QLabel('<font size="3"> Database Name: </font>')
        # self.hostname.addItems(LOGIN_ACCESS)

        self.port_no = QLineEdit()
        self.port_no.setText(str(self.port_number))
        self.port_noLabel = QLabel('<font size="3"> Port Number: </font>')
        # self.hostname.addItems(LOGIN_ACCESS)

        self.btn_Submit = QPushButton("Register", self)
        self.btn_Submit.clicked.connect(self.register_user)

        layout = QFormLayout()
        layout.addRow(self.UserLabel, self.userName)
        layout.addRow(self.PasswordLabel, self.passWord)
        # layout.addRow(self.PasswordLabel1, self.passWord1)
        layout.addRow(self.hostnameLabel, self.hostname)
        layout.addRow(self.dbnameLabel, self.dbname)
        layout.addRow(self.port_noLabel, self.port_no)
        layout.addRow(self.btn_Submit)

        self.setLayout(layout)

    def register_user(self):
        self.row_data = make_nested_dict()
        self.row_data['id'] = 1
        self.row_data['mysql_login'] = self.userName.text()
        self.row_data['mysql_passwd'] = self.passWord.text()
        self.row_data['mysql_dbname'] = self.dbname.text()
        self.row_data['mysql_hostname'] = self.hostname.text()
        self.row_data['mysql_port'] = self.port_no.text()
        self.accept()

        # uname=self.userName.text()
        # passwd=self.passWord.text()
        # passwd1=self.passWord1.text()
        # access=self.permission.currentText()

        # if str(passwd) == str(passwd1):
        #     check_db = Sign(self.rk_db)
        #     result = check_db.check_login_name(uname)
        #
        #     if result:
        #         registered=check_db.signup(uname, passwd, access)
        #         if registered:
        #             QMessageBox.information(
        #                 self, f"User Registered !', {uname} added  as new user")
        #
        #             self.accept()
        #         else:
        #             QMessageBox.critical(self, 'Failed to register', 'Could not register to database')
        #
        #     else:
        #         QMessageBox.critical(self, 'User name exists !', 'Try different user name..')
        # else:
        #     QMessageBox.critical(self, 'Error', 'password not matching')

        #
        # if connection :
        #     self.accept()
        # else:
        #     QMessageBox.warning(
        #         self, 'Error', 'Unknown user or password')

    def accept(self):
        super(update_mysql_login, self).accept()

    def get_inp(self):
        return self.row_data

# https://stackoverflow.com/questions/41117733/validation-of-a-password-python
