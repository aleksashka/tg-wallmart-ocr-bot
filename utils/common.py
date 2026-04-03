from datetime import datetime, timezone, timedelta


def generate_filename(extension="jpg", tz_offset=None):
    """
    Generates a filename based on the current time in YYYYMMDDTHHMMSS format.

    Args:
        extension (str): The file extension (default: "jpg").
        tz_offset (int/float): Timezone offset in hours (e.g., 3 for UTC+3).
                               If None, uses local system time.

    Returns:
        str: Formatted filename (e.g., 20260328T210140.jpg).
    """
    if tz_offset is not None:
        # Create a fixed timezone based on the provided hour offset
        tz = timezone(timedelta(hours=tz_offset))
        now = datetime.now(tz)
    else:
        # Use the local system time
        now = datetime.now()

    # Format the date and time as YYYYMMDDTHHMMSS
    timestamp = now.strftime("%Y%m%dT%H%M%S")

    return f"{timestamp}.{extension}"


if __name__ == '__main__':
    # Examples:
    print(generate_filename(tz_offset=-6))  # e.g., 20260328T210140.jpg (UTC+3)
    # print(generate_filename(tz_offset=0))  # e.g., 20260328T180140.jpg (UTC)
    # print(generate_filename())  # e.g., 20260328T140140.jpg (Local)
