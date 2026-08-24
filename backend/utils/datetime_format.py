# backend/utils/datetime_format.py
from datetime import datetime

def au_timestamp(dt: datetime) -> str:
    if not isinstance(dt, datetime):
        return ""
    return dt.strftime("%d-%m-%Y %H:%M")
