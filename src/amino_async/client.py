import json
import time
from typing import BinaryIO

import aiohttp

from .utils import objects, exceptions, helpers, device, headers


class Client:

    json: dict
    userId: str
    sid: str
    account: objects.UserProfile.UserProfile
    profile: objects.UserProfile.UserProfile

    def __init__(self):
        self.api = "https://service.narvii.com/api/v1"
        self.session = aiohttp.ClientSession()

        self.device = device.DeviceGenerator()
        self.user_agent = self.device.user_agent
        self.device_id = self.device.device_id
        self.device_id_sig = self.device.device_id_sig
        self.headers = headers.Headers(self.device)

    async def login_aminoapps(self, email, password):
        data = json.dumps({
            "auth_type": 0,
            "email": f"{email}",
            "recaptcha_challenge": "03AGdBq26dD6ppA9g1OH9_WKNAxYH0I75xHbr5dUm-U4K30TMQWaFhx-73x3kusXim_Ri7vJZuBL5GQ65WvGdMe_-jXaOcMeMEuH828-EvbX8tGTWz_K84eIBHzbEOhq1wm2viW7LG6qzKOWFJSnys6OqpO_BdblytI3Kop9SgKcT7x5_T6XkiA5kytMivnw8MuP_s_RFt4mJmTVFVnYNwEuwW1bzNukxb8LXovMY2H3o-bg8IpA_MAJMx-uFWfv7zDOM4n6-4j1mc_ZJFfu7ykIfAuo4xAFMo_D7yO9omPbPbRwhTejzGIb4a2wlOSCWc1Hmbj8zRShqPObD4hOjdHIDHirvlqCnUoQGcyiwowsZoSgU2LjTDJwXboU-fm-lbYM_6nOoz_8_woSwz_MZr3jyTzJMkz7tb15uDoMbWzcoBCg8ryiGStOuKmem-mjo1yhT0tU09UIsa",
            "recaptcha_version": "v3",
            "secret": password
        })
        response = requests.post("https://aminoapps.com/api/auth", data=data, headers={
            "accept": "*/*",
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
        })
        if json.loads(response.text)["result"].get("isMember") is None:
            raise Exception("Login failed")
        else:
            self.sid = response.cookies["sid"]
            self.userId = helpers.sid_to_uid(self.sid)
            self.headers.sid = self.sid
            return response

    async def login(self, email, password):
        data = json.dumps({
            "email": email,
            "v": 2,
            "secret": f"0 {password}",
            "deviceID": self.device_id,
            "clientType": 100,
            "action": "normal",
            "timestamp": int(time.time() * 1000)
        })
        result = await self.session.post(f"{self.api}/g/s/auth/login", headers=self.headers.headers(data=data), data=data)
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            self.json = await result.json()
            self.userId = self.json["auid"]
            self.sid = self.json["sid"]
            self.headers.sid = self.sid
            self.account = objects.UserProfile(self.json["account"]).UserProfile
            self.profile = objects.UserProfile(self.json["userProfile"]).UserProfile
            return await result.json()

    async def login_sid(self, SID: str):
        self.sid = SID
        self.userId = helpers.sid_to_uid(SID)
        self.account: objects.UserProfile = await self.get_user_info(self.userId)
        self.profile = self.account
        self.headers.sid = self.sid

    async def get_user_info(self, userId: str):
        result = await self.session.get(f"{self.api}/g/s/user-profile/{userId}", headers=self.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            json_result = await result.json()
            return objects.UserProfile(json_result["userProfile"]).UserProfile

    async def get_community_info(self, comId: str):
        result = await self.session.get(f"{self.api}/g/s-x{comId}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount", headers=self.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            json_result = await result.json()
            return objects.Community(json_result["community"]).Community

    async def upload_media(self, file: BinaryIO, file_type: str):
        if file_type == "audio":
            t = "audio/aac"
        elif file_type == "image":
            t = "image/jpg"
        else:
            raise exceptions.SpecifyType(file_type)
        data = file.read()
        result = await self.session.post(f"{self.api}/g/s/media/upload", data=data, headers=self.headers.headers(content_type=t, data=data))
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            json_result = await result.json()
            return json_result["mediaValue"]

    async def sub_clients(self, start: int = 0, size: int = 25):
        result = await self.session.get(f"{self.api}/g/s/community/joined?v=1&start={start}&size={size}", headers=self.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            json_result = await result.json()
            return objects.CommunityList(json_result["communityList"]).CommunityList

    async def join_community(self, comId: str, invitationId: str = None):
        data = {"timestamp": int(time.time() * 1000)}
        if invitationId:
            data["invitationId"] = invitationId
        data = json.dumps(data)
        result = await self.session.post(f"{self.api}/x{comId}/s/community/join", data=data, headers=self.headers.headers(data=data))
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return await result.json()

    async def edit_profile(self, nickname: str = None,
                           content: str = None,
                           icon: str = None,
                           backgroundColor: str = None,
                           backgroundImage: str = None,
                           defaultBubbleId: str = None):
        data = {
            "address": None,
            "latitude": 0,
            "longitude": 0,
            "mediaList": None,
            "eventSource": "UserProfileView",
            "timestamp": int(time.time() * 1000)
        }

        if nickname:
            data["nickname"] = nickname
        if icon:
            data["icon"] = icon
        if content:
            data["content"] = content
        if backgroundColor:
            data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
        if backgroundImage:
            data["extensions"] = {"style": {"backgroundMediaList": [[100, backgroundImage, None, None, None]]}}
        if defaultBubbleId:
            data["extensions"] = {"defaultBubbleId": defaultBubbleId}

        data = json.dumps(data)
        result = await self.session.post(f"{self.api}/g/s/user-profile/{self.userId}", headers=self.headers.headers(data=data), data=data)
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return result.json()

    async def get_wallet_info(self):
        result = await self.session.get(f"{self.api}/g/s/wallet", headers=self.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            json_result = await result.json()
            return objects.WalletInfo(json_result["wallet"]).WalletInfo

    async def get_wallet_history(self, start: int = 0, size: int = 25):
        result = await self.session.get(f"{self.api}/g/s/wallet/coin/history?start={start}&size={size}", headers=self.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            json_result = await result.json()
            return objects.WalletHistory(json_result["coinHistoryList"]).WalletHistory

    async def get_from_code(self, code: str):
        result = await self.session.get(f"{self.api}/g/s/link-resolution?q={code}", headers=self.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            json_result = await result.json()
            return objects.FromCode(json_result["linkInfoV2"]).FromCode

    async def get_from_id(self, objectId: str, objectType: int, comId: str = None):
        data = json.dumps({
            "objectId": objectId,
            "targetCode": 1,
            "objectType": objectType,
            "timestamp": int(time.time() * 1000)
        })

        if comId:
            result = await self.session.post(f"{self.api}/g/s-x{comId}/link-resolution", headers=self.headers.headers(data=data), data=data)
        else:
            result = await self.session.post(f"{self.api}/g/s/link-resolution", headers=self.headers.headers(data=data), data=data)
        if result.status != 200:
            return exceptions.CheckException(result.status)
        else:
            json_result = await result.json()
            return objects.FromCode(json_result["linkInfoV2"]).FromCode

    async def link_identify(self, code: str):
        result = await self.session.get(f"{self.api}/g/s/community/link-identify?q=http%3A%2F%2Faminoapps.com%2Finvite%2F{code}", headers=self.headers.headers())
        return await result.json()
