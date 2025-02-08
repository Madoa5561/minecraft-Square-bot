# -*- coding: utf-8 -*-
import requests


def loggedIn(func):
    def checkLogin(*args, **kwargs):
        if args[0].can_use_timeline_biz:
            return func(*args, **kwargs)
        else:
            raise Exception("can't use Timeline Biz func")

    return checkLogin


class TimelineBiz:
    can_use_timeline_biz = False

    def __init__(self):
        TIMELINE_BIZ_LIFF_ID = "1654109201-MgN2z4Nd"
        self.can_use_timeline_biz = False
        try:
            self.cmsToken = self.checkAndGetValue(self.issueLiffView(None, TIMELINE_BIZ_LIFF_ID), 7, 'val_7')
            #self.cmsSession = self.getCmsSession() #can't use Timeline Biz: HTTPSConnectionPool(host='timeline.line.biz', port=443): Max retries exceeded with url
            self.can_use_timeline_biz = True
        except Exception as e:
            self.log(f"Timeline Bizを使用できません: {e}")

    def getCmsSession(self):
        url = 'https://timeline.line.biz/api/auth/getSessionByIdToken?idToken=' + self.cmsToken
        req = requests.session()
        try:
            res = req.get(url)
            res.raise_for_status()
            self.can_use_timeline_biz = True
        except requests.exceptions.RequestException as e:
            raise Exception(f"failed to get Cms Session: {e}")
        return req

    @loggedIn
    def getLiffCert(self):
        url = 'https://api.line.me/oauth2/v2.1/certs'
        res = self.cmsSession.get(url, headers={"authorization": f"Bearer {self.cmsToken}"})
        return res.json()

    @loggedIn
    def getCmsUser(self):
        url = 'https://timeline.line.biz/api/cmsUser'
        res = self.cmsSession.get(url)
        return res.json()

    @loggedIn
    def getOAList(self):
        url = 'https://legy-jp.line-apps.com/api/timeline/v2/bot/list'
        res = self.cmsSession.get(url)
        return res.json()

    @loggedIn
    def createOA(self, displayName, count=100):
        url = 'https://legy-jp.line-apps.com/api/timeline/v2/bot/create'
        data = {
            "displayName": displayName,
            "category": 189,
            "statusMessage": "japanese Poeple"
        }
        headers = {
            'referer': 'https://legy-jp.line-apps.com/liff/liff-account/information-terms',
            'origin': 'https://legy-jp.line-apps.com',
            'user-agent': 'iphoneapp.line/14.13.1 (iPhone; U; CPU iOS 18_0 like Mac OS X; ja_JP; g)',
            'x-botcms-lastclickedelement': "",
            'x-botcms-scriptrevision': '1.0.0-rc',
            'x-requested-with': 'jp.naver.line.android',
            "x-xsrf-token": self.cmsSession.cookies['XSRF-TOKEN'],
            'content-type': 'application/json;charset=UTF-8'
        }
        bots = []
        for i in range(count):
            data['displayName'] = f"{displayName} - {i + 1}"
            res = self.cmsSession.post(url, json=data, headers=headers)
            bots.append(res.json())
        return bots
        # https://timeline.line.biz/api/auth/getSessionByIdToken?idToken= + liff token
        # https://timeline.line.biz/api/common/init
        # https://timeline.line.biz/api/cmsUser
        # https://api.line.me/oauth2/v2.1/verify?access_token=
        # https://timeline.line.biz/api/bots/%40491jpvse/timeline/v2/bot/bridge
        # url = f'https://timeline.line.biz/api/bots/{currentSearchId}/timeline/v2/comment'
        # url2 = f'https://timeline.line.biz/api/bots/{currentSearchId}/timeline/v2/like'
        # url3 = f'https://timeline.line.biz/api/bots/{currentSearchId}/issueInvitationUrl'
