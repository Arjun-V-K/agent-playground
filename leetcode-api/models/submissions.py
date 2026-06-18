from pydantic import BaseModel


class SubmissionResponse(BaseModel):
    title: str
    datetime: str
    status: str
    lang: str


class LcSubmission(BaseModel):
    title: str
    titleSlug: str
    timestamp: str
    statusDisplay: str
    lang: str


class LcRecentSubmissionList(BaseModel):
    recentSubmissionList: list[LcSubmission]


class LcRecentSubmissionListResponse(BaseModel):
    data: LcRecentSubmissionList
