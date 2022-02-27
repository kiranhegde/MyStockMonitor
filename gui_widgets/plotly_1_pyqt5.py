from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow
from plotly.graph_objects import Figure, Scatter
import plotly

import numpy as np


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        # some example data
        x = np.arange(1000)
        y = x ** 2

        # create the plotly figure
        fig = Figure(Scatter(x=x, y=y))

        # we create html code of the figure
        html = '<html><body>'
        html += plotly.offline.plot(fig, output_type='div', include_plotlyjs='cdn')
        html += '</body></html>'

        # we create an instance of QWebEngineView and set the html code
        plot_widget = QWebEngineView()
        plot_widget.setHtml(html)

        # set the QWebEngineView instance as main widget
        self.setCentralWidget(plot_widget)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
