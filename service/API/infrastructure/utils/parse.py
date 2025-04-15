from datetime import datetime


def parse_phone(value: str):
    return value.strip().replace("+", '').replace(' ', '')


def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False