#!/usr/bin/env python3

from aiohttp import ClientSession
from asyncio import sleep
from discord import Embed
from discord import AsyncWebhookAdapter

import logs.openLogs as log
import logs.status as status
from utils.webhooks import DiscordHooks

class Event():
  def __init__(self, eventName):
    self.eventName = eventName

  async def run(self, *callbackArgs):
    for manager in EventManager._managers:
      for event in manager._managedEvents:
        if event['eventName'] == self.eventName:
          await event['callbackFn'](*callbackArgs)

class EventManager():
  _managers = []

  def __init__(self):
    self._managers.append(self)
    self._managedEvents = []

  def manageEvent(self, eventName, callbackFn):
    self._managedEvents.append({
      'callbackFn': callbackFn,
      'eventName': eventName
    })

class RoyUB(EventManager):
  def __init__(self, client, mode = 'silent', hookId = '', hookToken = ''):
    self.webhook = {
      'id': hookId,
      'token': hookToken
    }
    self.mode = mode
    self.client = client
    EventManager.__init__(self)

  async def emitMemberTimeout(self, *callbackArgs):
    e = Event('memberTimeout')
    await e.run(*callbackArgs)

  async def memberTimeout(self, ctx, reason, duration):
    client = self.client
    print(client)
    print(client.tism.state)
    client.tism.setState('busy', False)
    client.tism.setState('busyWith', None)
    print(client.tism.state)

    client.tism.queue('angryAt', ctx.author.id, reason)
    if self.mode == 'verbal' and self.webhook['id'] and self.webhook['token']:
      await self.logToDiscord('you', duration)
    print(log.client_now_angry.format(client.nickname, ctx.author.name, duration, reason))
    print(client.tism.state)

    time = (60 * duration)
    await sleep(time)

    client.tism.dequeue('angryAt', ctx.author.id, reason)
    if self.mode == 'verbal':
      print(log.client_no_longer_angry.format(client.nickname, ctx.author.name))

  async def logToDiscord(self, *args):
    if self.webhook['id'] and self.webhook['token']:
      s = ClientSession()
      async with s:
        message=status.discord_webhook_log_moira_not_listening.format(self.client.nickname, *args)
        colourCode=0x7a2faf

        embed = Embed(
          color=colourCode,
          title=status.discord_webhook_log_moira_not_listening_title,
          description=message
        )
        log = DiscordHooks(
          self.webhook,
          AsyncWebhookAdapter(s)
        )
        await log.hook.send(
          embed=embed
        )
      await s.close()
