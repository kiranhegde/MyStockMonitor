import yfinance as yf
import datetime

sbi = yf.Ticker("SBIN.NS")
# print(sbi.info)

end_date=datetime.datetime.today().date()
start_date=end_date-datetime.timedelta(2*365)
# print(start_date)
# print(end_date)
price=sbi.history(start=start_date ,
                  end=end_date)
print(price.tail().to_string())
bsheet=sbi.actions
print(bsheet.head().to_string())