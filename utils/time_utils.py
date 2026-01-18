from datetime import datetime, timedelta, timezone
# from windtail_config import RESET_HOUR_UTC


def next_weekday_at_hour(weekday: int, hour: int) -> int:
    """
    Returns unix timestamp for the next occurrence of `weekday` at `hour` UTC.
    If today is the weekday, it returns TODAY at that hour (not next week).
    """
    now = datetime.now(timezone.utc)
    target = now.replace(hour=hour, minute=0, second=0, microsecond=0)

    days_ahead = (weekday - now.weekday()) % 7
    target += timedelta(days=days_ahead)

    return int(target.timestamp())


def next_reset_today_or_tomorrow(hour: int) -> int:
    """
    If reset time today hasn't passed, return today.
    Otherwise return tomorrow at reset hour.
    """
    now = datetime.now(timezone.utc)

    today = now.replace(hour=hour, minute=0, second=0, microsecond=0)

    if now < today:
        return int(today.timestamp())

    tomorrow = today + timedelta(days=1)
    return int(tomorrow.timestamp())


def next_thursday_and_sunday(hour: int) -> tuple[int, int]:
    thursday = next_weekday_at_hour(3, hour)
    sunday = next_weekday_at_hour(6, hour)
    return tuple(sorted((thursday, sunday)))
