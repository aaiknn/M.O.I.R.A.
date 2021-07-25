#!/usr/bin/env python3

from aiohttp import ClientSession
from discord import Embed
from discord import AsyncWebhookAdapter
from time import gmtime as timestamp

import logs.errors as ugh
import logs.status as status
from utils.webhooks import DiscordHooks

async def dbSelftest(self, startupErrors):
  try:
    selftest = await self.db.selfTest()
  except:
    print('Database isn\'t happy about your setup.')
  else:
    if not selftest:
      startupErrors.append(f'Error: {ugh.database_connection_error}')
      print(f'\nError: {ugh.database_connection_error}')

async def logStartup(id, token, warnings):
  s = ClientSession()
  async with s:
    t = timestamp()
    startUpMessage=f'It\'s true.\nUTC Timestamp: {t.tm_mday}-{t.tm_mon}-{t.tm_year} at {t.tm_hour}:{t.tm_min}:{t.tm_sec}.'
    if warnings:
      for warning in warnings:
        startUpMessage+=f'\n\n{warning}'

    embed = Embed(
      title=status.discord_webhook_log_moira_up,
      description=startUpMessage
    )
    log = DiscordHooks(
      id,
      token,
      AsyncWebhookAdapter(s)
    )
    await log.hook.send(
      embed=embed
    )
  await s.close()
