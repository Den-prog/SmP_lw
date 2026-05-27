import datetime
import re
import html

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

def match_cron_field(value, field_str):
    if field_str == '*':
        return True

    # Перевірка формату */X (наприклад, */5)
    m = re.match(r'^\*/(\d+)$', field_str)
    if m:
        return value % int(m.group(1)) == 0

    # Перевірка точного числа (наприклад, 15)
    if re.match(r'^\d+$', field_str):
        return value == int(field_str)

    return False


def is_valid_cron_syntax(cron_str):
    pattern = r'^(\*|\d+|\*/\d+)\s+(\*|\d+|\*/\d+)\s+(\*|\d+|\*/\d+)\s+(\*|\d+|\*/\d+)\s+(\*|\d+|\*/\d+)$'
    return bool(re.match(pattern, cron_str.strip()))

def is_cron_match(cron_str, dt):
    parts = cron_str.strip().split()
    if len(parts) != 5:
        return False

    # isoweekday: 1=Пн, ..., 7=Нд. У cron: 0=Нд, 1=Пн...
    weekday = 0 if dt.isoweekday() == 7 else dt.isoweekday()

    return (match_cron_field(dt.minute, parts[0]) and
            match_cron_field(dt.hour, parts[1]) and
            match_cron_field(dt.day, parts[2]) and
            match_cron_field(dt.month, parts[3]) and
            match_cron_field(weekday, parts[4]))


def is_valid_email(email_string):
    """Перевіряє, чи є рядок коректною email-адресою"""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email_string.strip()))

def text_to_html(text_string):
    """Базове перетворення звичайного тексту в HTML (наприклад, заміна переносів рядків)"""
    # Екрануємо базові HTML символи для безпеки (<, >, &)
    escaped_text = html.escape(text_string)
    # Замінюємо переноси рядків на теги <br>
    html_output = re.sub(r'\r?\n', '<br>\n', escaped_text)
    return html_output

def html_to_text(html_string):
    """Очищення HTML тегів з рядка для отримання чистого тексту"""
    # Видаляємо всі теги <...> за допомогою регулярного виразу
    text_without_tags = re.sub(r'<[^>]+>', '', html_string)
    # Декодуємо HTML сутності назад у звичайні символи (наприклад, &amp; у &)
    plain_text = html.unescape(text_without_tags)
    return plain_text