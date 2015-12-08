import calendar


def datetime_to_utc_timestamp(dt):
    return int(calendar.timegm(dt.utctimetuple()))


def datetime_to_utc_timestamp_millis(dt):
    return int(calendar.timegm(dt.utctimetuple()) * 1000 + dt.microsecond // 1000)


def datetime_to_csv_format(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]  # only keep 2 digits
