from datetime import datetime
import calendar


def report_period(date: str = None) -> tuple[str, str]:    # string - yyyy-mm-dd
    """
    Determines the two-month reporting period for a given date.
    If the date is within the first 5 days of a reporting period,
    it returns the previous period.
    Args:
        date (datetime, optional): The date to check. Defaults to today's date.
    Returns:
        tuple: (start_date, end_date) of the reporting period.
    """
    if date is None:
        date = datetime.today()
    else:
        date = datetime.strptime(date, '%Y-%m-%d')

    year, month, day = date.year, date.month, date.day

    # Determine the normal reporting period
    start_month = ((month - 1) // 2) * 2 + 1  # 1, 3, 5, 7, 9, 11
    end_month = start_month + 1

    # Adjust for beginning of period (first 10 days → return previous period)
    if day <= 10:
        start_month -= 2
        end_month -= 2

    # Adjust for year change if shifting to previous period
    if start_month < 1:
        start_month += 12
        end_month += 12
        year -= 1

    # Get last day of adjusted end_month
    last_day_of_end_month = calendar.monthrange(year, end_month)[1]

    # Adjusted start and end dates
    start_date = datetime(year, start_month, 1)
    end_date = datetime(year, end_month, last_day_of_end_month)

    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")



