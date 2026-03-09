def billing_anchor_friday_utc_unix_timestamp():
    """
    Calculate the next Friday at 00:00 UTC and return its Unix timestamp.
    """
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    if now.weekday() == 4:
        # If it's already Friday but before 00:00 UTC, return the current time
        return int(
            (now + timedelta(days=7))
            .replace(hour=0, minute=0, second=0, microsecond=0)
            .timestamp()
        )
    # Calculate how many days until the next Friday (weekday() returns 0 for Monday, ..., 6 for Sunday)
    days_until_friday = (4 - now.weekday()) % 7
    next_friday = now + timedelta(days=days_until_friday)
    # Set time to 00:00:00
    next_friday = next_friday.replace(hour=0, minute=0, second=0, microsecond=0)

    return int(next_friday.timestamp())
