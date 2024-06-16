
def parse_phone(value: str):
    return value.strip().replace("+", '').replace(' ', '')
