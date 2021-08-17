import random


class DeviceGenerator:
    def __init__(self):
        device = self.generate_device_info()
        self.user_agent = device["user_agent"]
        self.device_id = device["device_id"]

    def generate_device_info(self):
        return {
            "device_id": "22979010C1C50E5C05278E9F00E80E7CB98E8557B31A902665DE7A14DB3BE0F8D41440B99BD5FAD18D",
            "user_agent": f"Dalvik/2.1.0 (Linux; U; Android 8.0; SM-A{random.randint(100, 900)}x Build/greatltexx-user {random.randint(5, 9)}.0 NMF{random.randint(20, 50)}X {random.randint(2, 4)}00190{random.randint(10, 999)} release-keys; com.narvii.amino.master/2.0.2{random.randint(2000, 9000)})"
        }
