import datetime
import re

#level1 (1, 2)
def is_valid_url(url_string):
    pattern = r"^(https?:\/\/)?([\w\-]+(\.[\w\-]+)+)([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?$"
    return bool(re.match(pattern, url_string))

def is_valid_date(date_string):
    pattern = r"^(0[1-9]|[12]\d|3[01])\/(0[1-9]|1[0-2])\/(1[6-9]\d{2}|[2-9]\d{3})$"
    match = re.match(pattern, date_string.strip())
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))

        try:
            datetime.date(year, month, day)
            return True
        except ValueError:
            return False
    return False

#level2 (11, 14)

def day_of_week(date_string):
    pattern = r"^(0[1-9]|[12]\d|3[01])[\/\.-](0[1-9]|1[0-2])[\/\.-](\d{4})$"
    match = re.match(pattern, date_string.strip())

    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))

        try:
            date_obj = datetime.date(year, month, day)
            weekdays = [
                "Понеділок",
                "Вівторок",
                "Середа",
                "Четвер",
                "П'ятниця",
                "Субота",
                "Неділя"
            ]
            day_name = weekdays[date_obj.weekday()]
            return f"{date_string} is {day_name}"

        except ValueError:
            return "non existent date"

    return f"{date_string} is not a valid date"