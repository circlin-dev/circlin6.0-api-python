class PushHistory:
    def __init__(
            self,
            id: int or None,
            target_id: int,
            device_token: str,
            title: str,
            message: str,
            type: str or None,
            result: int,
            json: any,
            result_json: any
    ):
        self.id = id
        self.target_id = target_id
        self.device_token = device_token
        self.title = title
        self.message = message
        self.type = type
        self.result = result,
        self.json = json,
        self.result_json = result_json


class PushReservation:
    def __init__(self, id: int or None):
        self.id = id