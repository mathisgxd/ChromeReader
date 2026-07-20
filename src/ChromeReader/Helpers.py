import datetime as dt
import colorama
from colorama import Fore as color
import json

# Helper functions
def colored_text(text: str, color: str):
    return f"{color}{text}{colorama.Style.RESET_ALL}"

def chrome_time_to_datetime(chrome_time, epoch_start: dt.datetime = dt.datetime(1601, 1, 1)) -> dt.datetime | None:
    if chrome_time:
        return (epoch_start + dt.timedelta(microseconds=chrome_time)).replace(microsecond=0)
    return None

def chrome_time_to_timedelta(chrome_time) -> dt.timedelta | None:
    if chrome_time:
        return dt.timedelta(microseconds=chrome_time)
    return None

def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

colorama.init(autoreset=True)