class Headers:
    def __init__(self, device_info):
        self.device_id = device_info.device_id
        self.device_id_sig = device_info.device_id_sig
        self.user_agent = device_info.user_agent
        self.sid = None

    def headers(self, data=None, content_type=None):
        headers = {
            "NDCDEVICEID": self.device_id,
            "NDC-MSG-SIG": self.device_id_sig,
            "Accept-Language": "ru-UA",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": self.user_agent,
            "Host": "service.narvii.com",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive"
        }

        if data:
            headers["Content-Length"] = str(len(data))
        if self.sid:
            headers["NDCAUTH"] = f"sid={self.sid}"
        if content_type:
            headers["Content-Type"] = content_type
        return headers
