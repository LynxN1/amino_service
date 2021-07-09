import base64
import json
import time
from binascii import hexlify
from os import urandom
from typing import BinaryIO
from uuid import UUID

from . import Client
from .utils import exceptions, objects


class SubClient:
    def __init__(self, comId: str, client: Client):
        self.client = client
        self.comId = comId

    async def check_in(self, tz: str = -time.timezone // 1000):
        data = json.dumps({
            "timezone": tz,
            "timestamp": int(time.time() * 1000)
        })
        result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/check-in", headers=self.client.headers.headers(data=data), data=data)
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return await result.json()

    async def lottery(self, tz: str = -time.timezone // 1000):
        data = json.dumps({
            "timezone": tz,
            "timestamp": int(time.time() * 1000)
        })

        result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/check-in/lottery", headers=self.client.headers.headers(data=data), data=data)
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            json_result = await result.json()
            return objects.LotteryLog(json_result["lotteryLog"]).LotteryLog

    async def edit_profile(self, nickname: str = None,
                           content: str = None,
                           icon: str = None,
                           chatRequestPrivilege: str = None,
                           mediaList: list = None,
                           backgroundImage: str = None,
                           backgroundColor: str = None,
                           titles: list = None,
                           defaultBubbleId: str = None):
        data = {"timestamp": int(time.time() * 1000)}
        if nickname:
            data["nickname"] = nickname
        if icon:
            data["icon"] = icon
        if content:
            data["content"] = content
        if mediaList:
            data["mediaList"] = mediaList
        if chatRequestPrivilege:
            data["extensions"] = {"privilegeOfChatInviteRequest": chatRequestPrivilege}
        if backgroundImage:
            data["extensions"] = {"style": {"backgroundMediaList": [[100, backgroundImage, None, None, None]]}}
        if backgroundColor:
            data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
        if titles:
            data["extensions"] = {"customTitles": titles}
        if defaultBubbleId:
            data["extensions"] = {"defaultBubbleId": defaultBubbleId}
        data = json.dumps(data)
        result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/user-profile/{self.client.userId}", headers=self.client.headers.headers(data=data), data=data)
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return await result.json()

    async def get_chat_thread(self, chatId: str):
        result = await self.client.session.get(f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}", headers=self.client.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            json_result = await result.json()
            return objects.Thread(json_result["thread"]).Thread

    async def send_active_obj(self, startTime: int, endTime: int, optInAdsFlags: int = 2147483647, tz: int = -time.timezone // 1000):
        data = json.dumps({
            "userActiveTimeChunkList": [{
                "start": startTime,
                "end": endTime
            }],
            "optInAdsFlags": optInAdsFlags,
            "timezone": tz
        })
        result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/community/stats/user-active-time", headers=self.client.headers.headers(data=data), data=data)
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return await result.json()

    async def get_blog_info(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None):
        if blogId or quizId:
            if quizId is not None:
                blogId = quizId
            result = await self.client.session.get(f"{self.client.api}/x{self.comId}/s/blog/{blogId}", headers=self.client.headers.headers())
            if result.status != 200:
                json_result = await result.json()
                return exceptions.CheckException(json_result)
            else:
                return objects.GetBlogInfo(await result.json()).GetBlogInfo

        elif wikiId:
            result = await self.client.session.get(f"{self.client.api}/x{self.comId}/s/item/{wikiId}", headers=self.client.headers.headers())
            if result.status != 200:
                json_result = await result.json()
                return exceptions.CheckException(json_result)
            else:
                return objects.GetWikiInfo(await result.json()).GetWikiInfo

        elif fileId:
            result = await self.client.session.get(f"{self.client.api}/x{self.comId}/s/shared-folder/files/{fileId}", headers=self.client.headers.headers())
            if result.status != 200:
                json_result = await result.json()
                return exceptions.CheckException(json_result)
            else:
                json_result = await result.json()
                return objects.SharedFolderFile(json_result["file"]).SharedFolderFile
        else:
            raise exceptions.SpecifyType()

    async def get_chat_messages(self, chatId: str, size: int = 25, pageToken: str = None):
        if pageToken is not None:
            url = f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/message?v=2&pagingType=t&pageToken={pageToken}&size={size}"
        else:
            url = f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}"
        result = await self.client.session.get(url, headers=self.client.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return objects.GetMessages(await result.json()).GetMessages

    async def delete_message(self, chatId: str, messageId: str, asStaff: bool = False, reason: str = None):
        data = {
            "adminOpName": 102,
            # "adminOpNote": {"content": reason},
            "timestamp": int(time.time() * 1000)
        }
        if asStaff and reason:
            data["adminOpNote"] = {"content": reason}

        data = json.dumps(data)
        if not asStaff:
            result = await self.client.session.delete(f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}", headers=self.client.headers.headers())
        else:
            result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}/admin", headers=self.client.headers.headers(data=data), data=data)
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return await result.json()

    async def edit_chat(self, chatId: str,
                        doNotDisturb: bool = None,
                        pinChat: bool = None,
                        title: str = None,
                        icon: str = None,
                        backgroundImage: str = None,
                        content: str = None,
                        announcement: str = None,
                        coHosts: list = None,
                        keywords: list = None,
                        pinAnnouncement: bool = None,
                        publishToGlobal: bool = None,
                        canTip: bool = None,
                        viewOnly: bool = None,
                        canInvite: bool = None,
                        fansOnly: bool = None):
        data = {"timestamp": int(time.time() * 1000)}
        if title:
            data["title"] = title
        if content:
            data["content"] = content
        if icon:
            data["icon"] = icon
        if keywords:
            data["keywords"] = keywords
        if announcement:
            data["extensions"] = {"announcement": announcement}
        if pinAnnouncement:
            data["extensions"] = {"pinAnnouncement": pinAnnouncement}
        if fansOnly:
            data["extensions"] = {"fansOnly": fansOnly}
        if publishToGlobal:
            data["publishToGlobal"] = 1
        if not publishToGlobal:
            data["publishToGlobal"] = 0

        res = []

        if doNotDisturb is not None:
            if doNotDisturb:
                data = json.dumps({"alertOption": 2, "timestamp": int(time.time() * 1000)})
                result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.client.userId}/alert", data=data, headers=self.client.headers.headers(data=data))
                if result.status != 200:
                    json_result = await result.json()
                    res.append(exceptions.CheckException(json_result))
                else:
                    res.append(result.status)

            if not doNotDisturb:
                data = json.dumps({"alertOption": 1, "timestamp": int(time.time() * 1000)})
                result = await self.client.session.post(
                    f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.client.userId}/alert", data=data, headers=self.client.headers.headers(data=data))
                if result.status != 200:
                    json_result = await result.json()
                    res.append(exceptions.CheckException(json_result))
                else:
                    res.append(result.status)

        if pinChat is not None:
            if pinChat:
                result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/pin", data=data, headers=self.client.headers.headers())
                if result.status != 200:
                    json_result = await result.json()
                    res.append(exceptions.CheckException(json_result))
                else:
                    res.append(result.status)

            if not pinChat:
                result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/unpin", data=data, headers=self.client.headers.headers())
                if result.status != 200:
                    json_result = await result.json()
                    res.append(exceptions.CheckException(json_result))
                else:
                    res.append(result.status)

        if backgroundImage is not None:
            data = json.dumps({"media": [100, backgroundImage, None], "timestamp": int(time.time() * 1000)})
            result = await self.client.session.post(
                f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.client.userId}/background", data=data, headers=self.client.headers.headers(data=data))
            if result.status != 200:
                json_result = await result.json()
                res.append(exceptions.CheckException(json_result))
            else:
                res.append(result.status)

        if coHosts is not None:
            data = json.dumps({"uidList": coHosts, "timestamp": int(time.time() * 1000)})
            result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/co-host", data=data, headers=self.client.headers.headers(data=data))
            if result.status != 200:
                json_result = await result.json()
                res.append(exceptions.CheckException(json_result))
            else:
                res.append(result.status)

        if viewOnly is not None:
            if viewOnly:
                result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/view-only/enable", data=data, headers=self.client.headers.headers(data=data))
                if result.status != 200:
                    json_result = await result.json()
                    res.append(exceptions.CheckException(json_result))
                else:
                    res.append(result.status)

            if not viewOnly:
                result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/view-only/disable", data=data, headers=self.client.headers.headers(data=data))
                if result.status != 200:
                    json_result = await result.json()
                    res.append(exceptions.CheckException(json_result))
                else:
                    res.append(result.status)

        if canInvite is not None:
            if canInvite:
                result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/members-can-invite/enable", data=data, headers=self.client.headers.headers(data=data))
                if result.status != 200:
                    json_result = await result.json()
                    res.append(exceptions.CheckException(json_result))
                else:
                    res.append(result.status)

            if not canInvite:
                result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/members-can-invite/disable", data=data, headers=self.client.headers.headers(data=data))
                if result.status != 200:
                    json_result = await result.json()
                    res.append(exceptions.CheckException(json_result))
                else:
                    res.append(result.status)

        if canTip is not None:
            if canTip:
                result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/tipping-perm-status/enable", data=data, headers=self.client.headers.headers(data=data))
                if result.status != 200:
                    json_result = await result.json()
                    res.append(exceptions.CheckException(json_result))
                else:
                    res.append(result.status)

            if not canTip:
                result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/tipping-perm-status/disable", data=data, headers=self.client.headers.headers(data=data))
                if result.status != 200:
                    json_result = await result.json()
                    res.append(exceptions.CheckException(json_result))
                else:
                    res.append(result.status)

        data = json.dumps(data)
        result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}", headers=self.client.headers.headers(data=data), data=data)
        if result.status != 200:
            json_result = await result.json()
            res.append(exceptions.CheckException(json_result))
        else:
            res.append(result.status)

        return res

    async def get_quiz_rankings(self, quizId: str, start: int = 0, size: int = 25):
        result = await self.client.session.get(f"{self.client.api}/x{self.comId}/s/blog/{quizId}/quiz/result?start={start}&size={size}", headers=self.client.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return objects.QuizRankings(await result.json()).QuizRankings

    async def get_user_following(self, userId: str, start: int = 0, size: int = 25):
        result = await self.client.session.get(f"{self.client.api}/x{self.comId}/s/user-profile/{userId}/joined?start={start}&size={size}", headers=self.client.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            json_result = await result.json()
            return objects.UserProfileList(json_result["userProfileList"]).UserProfileList

    async def get_recent_blogs(self, pageToken: str = None, start: int = 0, size: int = 25):
        if pageToken is not None:
            url = f"{self.client.api}/x{self.comId}/s/feed/blog-all?pagingType=t&pageToken={pageToken}&size={size}"
        else:
            url = f"{self.client.api}/x{self.comId}/s/feed/blog-all?pagingType=t&start={start}&size={size}"

        result = await self.client.session.get(url, headers=self.client.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            json_result = await result.json()
            return objects.RecentBlogs(json_result).RecentBlogs

    async def comment(self, message: str,
                      userId: str = None,
                      blogId: str = None,
                      wikiId: str = None,
                      replyTo: str = None,
                      isGuest: bool = False):
        data = {
            "content": message,
            "stickerId": None,
            "type": 0,
            "timestamp": int(time.time() * 1000)
        }

        if replyTo:
            data["respondTo"] = replyTo

        if isGuest:
            comType = "g-comment"
        else:
            comType = "comment"

        if userId:
            data["eventSource"] = "UserProfileView"
            data = json.dumps(data)
            result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/user-profile/{userId}/{comType}", headers=self.client.headers.headers(data=data), data=data)

        elif blogId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/blog/{blogId}/{comType}", headers=self.client.headers.headers(data=data), data=data)

        elif wikiId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/item/{wikiId}/{comType}", headers=self.client.headers.headers(data=data), data=data)
        else:
            raise exceptions.SpecifyType()
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return await result.json()

    async def get_chat_users(self, chatId: str, start: int = 0, size: int = 25):
        result = await self.client.session.get(f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/member?start={start}&size={size}&type=default&cv=1.2", headers=self.client.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            json_result = await result.json()
            return objects.UserProfileList(json_result["memberList"]).UserProfileList

    async def get_blocker_users(self, start: int = 0, size: int = 25):
        result = await self.client.session.get(f"{self.client.api}/x{self.comId}/s/block/full-list?start={start}&size={size}", headers=self.client.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            json_result = await result.json()
            return json.loads(str(json_result).replace("\'", "\""))["blockerUidList"]

    async def start_chat(self, userId: [str, list], message: str, title: str = None, content: str = None, isGlobal: bool = False, publishToGlobal: bool = False):
        if isinstance(userId, str):
            userIds = [userId]
        elif isinstance(userId, list):
            userIds = userId
        else:
            raise exceptions.WrongType(type(userId))
        data = {
            "title": title,
            "inviteeUids": userIds,
            "initialMessageContent": message,
            "content": content,
            "timestamp": int(time.time() * 1000)
        }
        if isGlobal is True:
            data["type"] = 2
            data["eventSource"] = "GlobalComposeMenu"
        else:
            data["type"] = 0
        if publishToGlobal is True:
            data["publishToGlobal"] = 1
        else:
            data["publishToGlobal"] = 0
        data = json.dumps(data)
        result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/chat/thread", data=data, headers=self.client.headers.headers(data=data))
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return await result.json()

    async def invite_to_chat(self, userId: [str, list], chatId: str):
        if isinstance(userId, str):
            userIds = [userId]
        elif isinstance(userId, list):
            userIds = userId
        else:
            raise exceptions.WrongType(type(userId))
        data = json.dumps({
            "uids": userIds,
            "timestamp": int(time.time() * 1000)
        })
        result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/member/invite", headers=self.client.headers.headers(data=data), data=data)
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return await result.json()

    async def send_coins(self, coins: int, blogId: str = None, chatId: str = None, objectId: str = None, transactionId: str = None):
        url = None
        if transactionId is None:
            transactionId = str(UUID(hexlify(urandom(16)).decode('ascii')))

        data = {
            "coins": coins,
            "tippingContext": {"transactionId": transactionId},
            "timestamp": int(time.time() * 1000)
        }

        if blogId is not None:
            url = f"{self.client.api}/x{self.comId}/s/blog/{blogId}/tipping"
        if chatId is not None:
            url = f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/tipping"
        if objectId is not None:
            data["objectId"] = objectId
            data["objectType"] = 2
            url = f"{self.client.api}/x{self.comId}/s/tipping"
        if url is None:
            raise exceptions.SpecifyType()
        data = json.dumps(data)
        result = await self.client.session.post(url, headers=self.client.headers.headers(data=data), data=data)
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return await result.json()

    async def follow(self, userId: [str, list]):
        if isinstance(userId, str):
            result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/user-profile/{userId}/member", headers=self.client.headers.headers())
        elif isinstance(userId, list):
            data = json.dumps({"targetUidList": userId, "timestamp": int(time.time() * 1000)})
            result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/user-profile/{self.client.userId}/joined", headers=self.client.headers.headers(data=data), data=data)
        else:
            raise exceptions.WrongType(type(userId))

        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return await result.json()

    async def unfollow(self, userId: str):
        result = await self.client.session.delete(f"{self.client.api}/x{self.comId}/s/user-profile/{self.client.userId}/joined/{userId}", headers=self.client.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return await result.json()

    async def send_message(self, message: str = None,
                           messageType: int = 0,
                           chatId: str = None,
                           file: BinaryIO = None,
                           fileType: str = None,
                           replyTo: str = None,
                           mentionUserIds: list = None,
                           stickerId: str = None,
                           embedId: str = None,
                           embedType: int = None,
                           embedLink: str = None,
                           embedTitle: str = None,
                           embedContent: str = None,
                           embedImage: BinaryIO = None,
                           refId: int = int(time.time() / 10 % 1000000000)):
        if message is not None and file is None:
            message = message.replace("<$", "‎‏").replace("$>", "‬‭")

        mentions = []
        if mentionUserIds:
            for mention_uid in mentionUserIds:
                mentions.append({"uid": mention_uid})

        if embedImage:
            embedImage = [[100, self.client.upload_media(embedImage, "image"), None]]

        data = {
            "type": messageType,
            "content": message,
            "clientRefId": refId,
            "attachedObject": {
                "objectId": embedId,
                "objectType": embedType,
                "link": embedLink,
                "title": embedTitle,
                "content": embedContent,
                "mediaList": embedImage
            },
            "extensions": {"mentionedArray": mentions},
            "timestamp": int(time.time() * 1000)
        }

        if replyTo:
            data["replyMessageId"] = replyTo

        if stickerId:
            data["content"] = None
            data["stickerId"] = stickerId
            data["type"] = 3

        if file:
            data["content"] = None
            if fileType == "audio":
                data["type"] = 2
                data["mediaType"] = 110

            elif fileType == "image":
                data["mediaType"] = 100
                data["mediaUploadValueContentType"] = "image/jpg"
                data["mediaUhqEnabled"] = True

            elif fileType == "gif":
                data["mediaType"] = 100
                data["mediaUploadValueContentType"] = "image/gif"
                data["mediaUhqEnabled"] = True

            else:
                raise exceptions.SpecifyType(fileType)

            data["mediaUploadValue"] = base64.b64encode(file.read()).decode()

        data = json.dumps(data)
        result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/message", headers=self.client.headers.headers(data=data), data=data)
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return await result.json()

    async def play_quiz(self, quizId: str, questionIdsList: list, answerIdsList: list, quizMode: int = 0):
        quizAnswerList = []
        for question, answer in zip(questionIdsList, answerIdsList):
            part = json.dumps({
                "optIdList": [answer],
                "quizQuestionId": question,
                "timeSpent": 0.0
            })
            quizAnswerList.append(json.loads(part))
        data = json.dumps({
            "mode": quizMode,
            "quizAnswerList": quizAnswerList,
            "timestamp": int(time.time() * 1000)
        })
        result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/blog/{quizId}/quiz/result", headers=self.client.headers.headers(data=data), data=data)
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return await result.json()

    async def like_blog(self, blogId: [str, list] = None, wikiId: str = None):
        data = {
            "value": 4,
            "timestamp": int(time.time() * 1000)
        }
        if blogId:
            if isinstance(blogId, str):
                data["eventSource"] = "UserProfileView"
                data = json.dumps(data)
                result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/blog/{blogId}/vote?cv=1.2", headers=self.client.headers.headers(data=data), data=data)
            elif isinstance(blogId, list):
                data["targetIdList"] = blogId
                data = json.dumps(data)
                result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/feed/vote", headers=self.client.headers.headers(data=data), data=data)
            else:
                raise exceptions.WrongType
        elif wikiId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/item/{wikiId}/vote?cv=1.2", headers=self.client.headers.headers(data=data), data=data)
        else:
            raise exceptions.SpecifyType()
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return await result.json()

    async def join_chat(self, chatId: str):
        result = await self.client.session.post(f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.client.userId}", headers=self.client.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return await result.json()

    async def leave_chat(self, chatId: str):
        result = await self.client.session.delete(f"{self.client.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.client.userId}", headers=self.client.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return await result.json()

    async def get_all_users(self, type: str = "recent", start: int = 0, size: int = 25):
        if type == "recent":
            result = await self.client.session.get(f"{self.client.api}/x{self.comId}/s/user-profile?type=recent&start={start}&size={size}", headers=self.client.headers.headers())
        elif type == "banned":
            result = await self.client.session.get(f"{self.client.api}/x{self.comId}/s/user-profile?type=banned&start={start}&size={size}", headers=self.client.headers.headers())
        elif type == "featured":
            result = await self.client.session.get(f"{self.client.api}/x{self.comId}/s/user-profile?type=featured&start={start}&size={size}", headers=self.client.headers.headers())
        elif type == "leaders":
            result = await self.client.session.get(f"{self.client.api}/x{self.comId}/s/user-profile?type=leaders&start={start}&size={size}", headers=self.client.headers.headers())
        elif type == "curators":
            result = await self.client.session.get(f"{self.client.api}/x{self.comId}/s/user-profile?type=curators&start={start}&size={size}", headers=self.client.headers.headers())
        else:
            raise exceptions.WrongType(type)
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return objects.UserProfileCountList(await result.json()).UserProfileCountList

    async def get_online_users(self, start: int = 0, size: int = 25):
        result = await self.client.session.get(f"{self.client.api}/x{self.comId}/s/live-layer?topic=ndtopic:x{self.comId}:online-members&start={start}&size={size}", headers=self.client.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            return objects.UserProfileCountList(await result.json()).UserProfileCountList

    async def get_user_info(self, userId: str):
        result = await self.client.session.get(f"{self.client.api}/x{self.comId}/s/user-profile/{userId}", headers=self.client.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            json_result = await result.json()
            return objects.UserProfile(json_result["userProfile"]).UserProfile

    async def get_user_followers(self, userId: str, start: int = 0, size: int = 25):
        result = await self.client.session.get(f"{self.client.api}/x{self.comId}/s/user-profile/{userId}/member?start={start}&size={size}", headers=self.client.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            json_result = await result.json()
            return objects.UserProfileList(json_result["userProfileList"]).UserProfileList

    async def get_chat_threads(self, start: int = 0, size: int = 25):
        result = await self.client.session.get(f"{self.client.api}/x{self.comId}/s/chat/thread?type=joined-me&start={start}&size={size}", headers=self.client.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            json_result = await result.json()
            return objects.ThreadList(json_result["threadList"]).ThreadList

    async def get_public_chat_threads(self, type: str = "recommended", start: int = 0, size: int = 25):
        result = await self.client.session.get(f"{self.client.api}/x{self.comId}/s/chat/thread?type=public-all&filterType={type}&start={start}&size={size}", headers=self.client.headers.headers())
        if result.status != 200:
            json_result = await result.json()
            return exceptions.CheckException(json_result)
        else:
            json_result = await result.json()
            return objects.ThreadList(json_result["threadList"]).ThreadList
