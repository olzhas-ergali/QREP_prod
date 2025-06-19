from datetime import datetime


def parse_phone(value: str):
    return value.strip().replace("+", '').replace(' ', '')


async def parse_date(date):
    formats = [
        "%d.%m.%Y",
        "%Y-%m-%d"
    ]
    for ftm in formats:
        try:
            d = datetime.strptime(date, ftm)
            return d
        except ValueError:
            pass
    return None


def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False