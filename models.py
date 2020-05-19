import faust


class APIRequest(faust.Record):
    user_id: str
    path: str
