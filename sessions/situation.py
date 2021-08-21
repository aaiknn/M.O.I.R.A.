#!/usr/bin/env python3

from aiohttp import ClientSession
from discord import Embed
from discord import AsyncWebhookAdapter
from typing import List

from logs import errors as err
import phrases.system as syx
from utils.general import getTermStyle
from sessions.exceptions import WebhookException
from utils.webhooks import DiscordHooks

class Situation:
  def __init__(self, **options):
    self.noColour   = options.get('noColour')

    self.errors     = options.get('errors')
    self.exceptions = options.get('exceptions')
    self.status     = options.get('status')
    self.warnings   = options.get('warnings')

  def resetAll(self):
    self.resetErrors()
    self.resetExceptions()
    self.resetStatus()
    self.resetWarnings()

  def resetErrors(self):
    self.errors = []

  def resetExceptions(self):
    self.exceptions = []

  def resetStatus(self):
    self.status = []

  def resetWarnings(self):
    self.warnings = []

  async def log(self, **options):
    title         = options.get('title')
    messageStart  = options.get('messageStart')
    webhook       = options.get('webhook')

    if not title:
      title       = syx.situation_log_fallback_title

    if webhook['id'] and webhook['token']:
      await self.logToDiscord(webhook, title=title, messageStart=messageStart)

    self.logToTerm(title=title, messageStart=messageStart)

  async def logIfNecessary(self, **options):
    need = False

    for prop, val in vars(self).items():
      if isinstance(val, List) and len(val) > 0:
        need = True
        break

    if need:
      await self.log(**options)

  def logToTerm(self, **options):
    title         = options.get('title')
    noColour      = self.noColour
    messageStart  = options.get('messageStart')

    boldred       = getTermStyle('boldred', noColour)
    boldyellow    = getTermStyle('boldyellow', noColour)
    bold          = getTermStyle('bold', noColour)
    colourend     = getTermStyle('colourend', noColour)

    if title:
      description = f'{title}\n'
    else:
      description = ''

    if messageStart:
      description += f'{messageStart}\n'

    for e in self.exceptions:
      description += f'\n{boldred}{syx.exception}:{colourend} {e}'

    for f in self.errors:
      description += f'\n{boldred}{syx.error}:{colourend} {f}'

    for meh in self.warnings:
      description += f'\n{boldyellow}{syx.warning}:{colourend} {meh}'

    for fact in self.status:
      description += f'\n{bold}{syx.status}:{colourend} {fact}'

    print(description)

  async def logToDiscord(self, webhook, **options):
    if not webhook:
      raise WebhookException(err.discord_logging_webhook_missing)

    title         = options.get('title')
    messageStart  = options.get('messageStart')

    if messageStart:
      description = f'{messageStart}'
    else:
      description = ''

    s = ClientSession()
    async with s:
      colourCode      = 0x7a2faf
      if len(self.warnings) > 0:
        colourCode    = 0xfffa38
      if len(self.errors) > 0 or len(self.exceptions) > 0:
        colourCode    = 0xff4238

      for e in self.exceptions:
        description += f'\n\n```diff\n- {syx.exception} -\n```\n{e}'

      for f in self.errors:
        description += f'\n\n```diff\n- {syx.error} -\n```\n{f}'

      for meh in self.warnings:
        description += f'\n\n```fix\n- {syx.warning} -\n```\n{meh}'

      for fact in self.status:
        description += f'\n\n```txt\n- {syx.status} -\n```\n{fact}'

      embed = Embed(
        color=colourCode,
        title=title,
        description=description
      )
      log = DiscordHooks(
        webhook,
        AsyncWebhookAdapter(s)
      )
      await log.hook.send(
        embed=embed
      )
    await s.close()

class SessionSituation(Situation):
  def __init__(self, **options):
    super().__init__(**options)

    self.channelId    = options.get('channelId')
    self.handler      = options.get('handler')
    self.sessionUser  = options.get('sessionUser')
    self.userMessage  = options.get('userMessage')
