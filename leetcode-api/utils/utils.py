from datetime import datetime


def unix_to_readable(timestamp: str) -> str:
    return datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M:%S")
