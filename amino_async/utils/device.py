import random
from hashlib import sha1
from secrets import token_hex


class DeviceGenerator:
    def __init__(self):
        device = self.generate_device_info()
        self.user_agent = device["user_agent"]
        self.device_id = device["device_id"]
        self.device_id_sig = device["device_id_sig"]

    def get_device_id(self):
        while True:
            hardware_info = token_hex(20).upper()
            device_id = '01' + hardware_info + sha1(bytes.fromhex('01' + hardware_info + "E9AF2D7F431E87A4F8C7B6F45EFC04B7E5F0EA4F")).hexdigest()
            return str(device_id.upper())

    def generate_device_info(self):
        return {
            "device_id": self.get_device_id(),
            "device_id_sig": "Aa0ZDPOEgjt1EhyVYyZ5FgSZSqJt",
            "user_agent": f"Dalvik/2.1.0 (Linux; U; Android 8.0; SM-A{random.randint(100, 900)}x Build/greatltexx-user {random.randint(5, 9)}.0 NMF{random.randint(20, 50)}X {random.randint(2, 4)}00190{random.randint(10, 999)} release-keys; com.narvii.amino.master/2.0.2{random.randint(2000, 9000)})"
        }
