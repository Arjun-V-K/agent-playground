import requests
from models.submissions import LcRecentSubmissionListResponse

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"


def get_recent_submissions(username: str) -> LcRecentSubmissionListResponse:
    query = """
    query recentSubmissionList($username: String!) {
      recentSubmissionList(username: $username) {
        title
        titleSlug
        timestamp
        statusDisplay
        lang
      }
    }
    """

    payload = {"query": query, "variables": {"username": username}}

    response = requests.post(LEETCODE_GRAPHQL_URL, json=payload, timeout=10)

    response.raise_for_status()

    return LcRecentSubmissionListResponse(**response.json())
