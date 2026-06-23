import requests
from langchain.tools import tool


@tool
def multiply(a: int, b: int) -> int:
    """
    Multiplies two numbers
    """
    return a * b


@tool
def get_user_submissions(username: str, date: str) -> str:
    """
    Fetch recent leetcode submissions for a user for given date.
    `date` should be an ISO date string like '2026-06-18'.
    """
    try:
        url = f"http://localhost:8001/users/{username}/submissions/{date}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return f"error: {e}"
