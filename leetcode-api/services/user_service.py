from datetime import date, datetime

from clients import leetcode_client
from models.submissions import LcRecentSubmissionListResponse, SubmissionResponse
from utils import utils


def get_recent_submissions(username: str, in_date: date) -> list[SubmissionResponse]:
    lc_output: LcRecentSubmissionListResponse = leetcode_client.get_recent_submissions(
        username
    )
    return [
        SubmissionResponse(
            title=item.title,
            status=item.statusDisplay,
            lang=item.lang,
            datetime=utils.unix_to_readable(item.timestamp),
        )
        for item in lc_output.data.recentSubmissionList
        if datetime.fromtimestamp(int(item.timestamp)).date() == in_date
    ]
