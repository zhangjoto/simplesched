#!/usr/bin/env python
#
# Author: Zhang Zhen
# E-Mail: zhangjoto@gmail.com
#
# Create Date: 2018-09-15
#

import requests


class BearyChatSender:
    """将消息发送到倍洽 Incoming 机器人。

    发送时可以 channel 指定接收消息的讨论组名字，Incoming 机器人的
    WebHook 地址由外部调用者直接设置 self.url 即可。"""
    def send(self, rcver, pack):
        pack = {'text': pack, 'channel': rcver}
        resp = requests.post(self.url, json=pack)
        if resp.status_code != 200:
            print(resp.status_code, resp.text)


class RocketChatSender:
    """将消息发送到 Rocket.Chat Incoming 机器人。

    发送时可以 channel 指定消息的接收者：
        - #channel 发送到指定频道
        - @user 发送到指定用户
        - XXXXXXXXXXXX 发送到指定讨论组，讨论组 ID 需要从管理界面上查询获取。

    WebHook 地址由外部调用者直接设置 self.url 即可。"""
    def send(self, rcver, pack):
        pack = {'text': pack, 'channel': rcver}
        resp = requests.post(self.url, json=pack)
        if resp.status_code != 200:
            print(resp.status_code, resp.text)
