import datetime
from service.API.infrastructure.utils.calendar import vacations_days


def get_fact_days_vacation(
        date_start: datetime.datetime,
        date_end: datetime.datetime,
):
    days_count = 0
    while True:
        if date_start > date_end:
            break
        if date_start not in vacations_days:
            days_count += 1
        date_start = date_start + datetime.timedelta(days=1)
    return days_count


def get_work_days_vacation(
        date_start: datetime.datetime,
        date_end: datetime.datetime,
):
    days_count = 0
    while True:
        if date_start > date_end:
            break
        if date_start not in vacations_days and date_start.weekday() not in [5, 6]:
            days_count += 1
        date_start = date_start + datetime.timedelta(days=1)
    return days_count


async def parse_date(date):
    formats = [
        "%d-%m-%Y %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%d.%m.%Y",
        "%d.%m.%Y %H:%M:%S",
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%d-%m-%Y",
        "%d-%m-%Y %H:%M:%S"
    ]
    for ftm in formats:
        try:
            d = datetime.datetime.strptime(date, ftm)
            return d
        except Exception as ex:
            pass
    raise ValueError(f"Не найден формат для даты {date}")
