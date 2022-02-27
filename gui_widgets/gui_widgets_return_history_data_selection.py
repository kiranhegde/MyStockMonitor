from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QRadioButton, QDialogButtonBox


class return_history_range_selection(QDialog):
    def __init__(self, plot_all_returns_history, parent=None):
        super(return_history_range_selection, self).__init__(parent)

        self.setWindowTitle('Market value time range selection')
        self.setWindowIcon(QIcon('icons/new_user.png'))
        self.resize(300, 150)
        self.plot_all_returns_history = plot_all_returns_history
        self.historic_portfolio_string = "Complete protfolio"
        self.current_portfolio_string = "Only current protfolio"
        self.current_only = True

        self.all_portfolio_button = QRadioButton(self.historic_portfolio_string)
        if self.plot_all_returns_history:
            self.all_portfolio_button.setChecked(self.plot_all_returns_history)
            self.current_only = False

        self.all_portfolio_button.toggled.connect(lambda: self.check_status(self.all_portfolio_button))

        self.current_only_button = QRadioButton(self.current_portfolio_string)
        self.current_only_button.toggled.connect(lambda: self.check_status(self.current_only_button))
        if self.current_only:
            self.current_only_button.setChecked(self.current_only)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        # self.resets = QPushButton("Reset")
        # self.resets.clicked.connect(self.clearAll)
        # self.buttonBox.addButton(self.resets, QDialogButtonBox.ResetRole)
        self.buttonBox.accepted.connect(self.accept)
        # self.buttonBox.closeEvent.connect(self.close)
        self.buttonBox.rejected.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.all_portfolio_button)
        layout.addWidget(self.current_only_button)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def check_status(self, button):
        if button.text() == self.historic_portfolio_string:
            self.plot_all_returns_history = True
            # print(button.text())

        if button.text() == self.current_portfolio_string:
            self.plot_all_returns_history = False
            # print(button.text())

    def accept(self):
        self.out = self.plot_all_returns_history
        # print("Plot all data ?",self.out)
        super(return_history_range_selection, self).accept()

    def get_inp(self):
        return self.out


#
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
