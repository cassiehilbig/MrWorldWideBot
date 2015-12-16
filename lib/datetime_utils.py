import calendar


def datetime_to_utc_timestamp_millis(dt):
    return int(calendar.timegm(dt.utctimetuple()) * 1000 + dt.microsecond // 1000)
