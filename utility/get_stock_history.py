# https://analyticsindiamag.com/top-python-libraries-to-get-historical-stock-data-with-code/
# https://analyticsindiamag.com/top-python-libraries-to-get-historical-stock-data-with-code/
from twelvedata import TDClient
# Initialize client
td = TDClient(apikey='7ed56cd8c25644049add02214809cf4f')
# Construct the necessary time serie
ts = td.time_series(
   symbol="MSFT",
   interval="1day",
   outputsize=500,)
# returns Plotly dash
ts.as_plotly_figure().show()