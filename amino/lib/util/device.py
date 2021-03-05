import random


class DeviceGenerator:
    def __init__(self):
        device = self.generate_device_info()
        self.user_agent = device["user_agent"]
        self.device_id = device["device_id"]
        self.device_id_sig = device["device_id_sig"]

    @staticmethod
    def generate_device_info():
        return {
            "device_id": "01C2A4FBDFFE4EF0FA865FBE1C2E01A3AE74547DDB227F60840680E90AA9EF709FBA294E6FAF7EDEEF",
            "device_id_sig": "Aa0ZDPOEgjt1EhyVYyZ5FgSZSqJt",
            "user_agent": f"Dalvik/2.1.0 (Linux; U; Android 8.0; SM-A{random.randint(100, 900)}x Build/greatltexx-user {random.randint(5, 9)}.0 NMF{random.randint(20, 50)}X {random.randint(2, 4)}00190{random.randint(10, 999)} release-keys; com.narvii.amino.master/2.0.2{random.randint(2000, 9000)})"
        }
