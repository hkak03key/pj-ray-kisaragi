from datetime import datetime as dt
from datetime import timezone as tz
from datetime import timedelta as td


def get_jst_date(date_str):
    d = dt.fromisoformat(date_str.replace("Z", "+00:00"))
    return d.astimezone(tz(td(hours=+9))).date()

