import re

def is_valid_url(url_string):
    pattern = r"^(https?:\/\/)?([\w\-]+(\.[\w\-]+)+)([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?$"
    return bool(re.match(pattern, url_string))

def is_valid_date(date_string):
    pattern = r"^(0[1-9]|[12]\d|3[01])\/(0[1-9]|1[0-2])\/(1[6-9]\d{2}|[2-9]\d{3})$"
    return bool(re.match(pattern, date_string))