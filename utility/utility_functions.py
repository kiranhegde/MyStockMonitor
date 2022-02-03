from PyQt5.QtCore import QDate
import ast


def get_statementNameByDate(name,bill_day=None):

    if bill_day:
        return str(name)+bill_day.toString('dd_MM_yyyy')
    else:
        now = QDate.currentDate()
        return str(name)+now.toString('dd_MM_yyyy')

class make_nested_dict(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

def reception_payin_bill_parse(billname):
    from DataBase.label_names import HOSPITAL_BILL_PAYIN_PREFIX,HOSPITAL_BILL_PREFIX,HOSPITAL_BILL_PAYOUT_PREFIX

    billdate = billname.split(HOSPITAL_BILL_PAYIN_PREFIX)[1]
    billname = billname.replace(HOSPITAL_BILL_PAYIN_PREFIX, HOSPITAL_BILL_PREFIX).replace('_', '-')
    bill_payout = HOSPITAL_BILL_PAYOUT_PREFIX + billdate

    return billdate,billname,bill_payout,


def date_time_range_full_day0(input_date):
    start_time=input_date+" 00:00:00"
    end_time=input_date +" 23:59:00"
    return start_time,end_time


def date_time_day_start_end(date_time):
    # date_time   is in date.date.now()
    start_time = date_time.replace(hour=0, minute=0, second=0)
    end_time = date_time.replace(hour=23, minute=59, second=50)
    return start_time,end_time





def parse_str(s):
   try:
      return ast.literal_eval(str(s))
   except:
      return str(s)