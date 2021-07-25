#!/usr/bin/env python3

from aiohttp import ClientSession
from discord import Embed
from discord import AsyncWebhookAdapter
from time import gmtime as timestamp

import logs.errors as ugh
import logs.status as status
from utils.webhooks import DiscordHooks

async def dbSelftest(self, scopedErrors):
  try:
    selftest = await self.db.selfTest()
  except ConnectionAbortedError:
    return False
  except:
    return False
  else:
    if not selftest:
      scopedErrors.append(ugh.database_connection_error)
      return False

    return True

async def logStartupToDiscord(id, token, scopedErrors, scopedWarnings):
  s = ClientSession()
  async with s:
    t = timestamp()
    startUpMessage=status.discord_webhook_log_moira_up_message.format(t)
    if scopedErrors or scopedWarnings:
      for error in scopedErrors:
        startUpMessage+=f'\n\n```diff\n- Error:\n```\n{error}'

      for warning in scopedWarnings:
        startUpMessage+=f'\n\n```fix\n- Warning:\n```\n{warning}'

    embed = Embed(
      title=status.discord_webhook_log_moira_up_title,
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
