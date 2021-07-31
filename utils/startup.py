#!/usr/bin/env python3

from aiohttp import ClientSession
from discord import Embed
from discord import AsyncWebhookAdapter
from time import gmtime as timestamp

import logs.errors as ugh
import logs.status as status
from utils.general import getTermColour
from utils.webhooks import DiscordHooks

async def dbSelftest(self, scopedErrors):
  try:
    selftest = await self.db.selfTest()
  except ConnectionAbortedError:
    self.tism.setSystemState('DB', 'DOWN')
    scopedErrors.append(ugh.database_connection_aborted_error)
  except:
    self.tism.setSystemState('DB', 'DOWN')
    scopedErrors.append(ugh.database_connection_error)
  else:
    if not selftest:
      self.tism.setSystemState('DB', 'DOWN')
      scopedErrors.append(ugh.database_connection_error_unknown)
    else:
      self.tism.setSystemState('DB', 'UP')

async def logTests(noColour, scopedErrors, scopedWarnings, webhook):
  boldred = getTermColour('boldred', noColour)
  boldyellow = getTermColour('boldyellow', noColour)
  colourend = getTermColour('colourend', noColour)

  for f in scopedErrors:
    print(f'\n{boldred}Error:{colourend} {f}')

  for huh in scopedWarnings:
    print(f'\n{boldyellow}Warning:{colourend} {huh}')

  if webhook['id'] and webhook['token']:
    await logStartupToDiscord(webhook, scopedErrors, scopedWarnings)

async def logStartupToDiscord(webhook, scopedErrors, scopedWarnings):
  s = ClientSession()
  async with s:
    t = timestamp()
    startUpMessage=status.discord_webhook_log_moira_up_message.format(t)
    colourCode=0x7a2faf
    if len(scopedWarnings) > 0:
      colourCode=0xfffa38
    if len(scopedErrors) > 0:
      colourCode=0xff4238

    if scopedErrors or scopedWarnings:
      for error in scopedErrors:
        startUpMessage+=f'\n\n```diff\n- Error -\n```\n{error}'

      for warning in scopedWarnings:
        startUpMessage+=f'\n\n```fix\n- Warning -\n```\n{warning}'

    embed = Embed(
      color=colourCode,
      title=status.discord_webhook_log_moira_up_title,
      description=startUpMessage
    )
    log = DiscordHooks(
      webhook,
      AsyncWebhookAdapter(s)
    )
    await log.hook.send(
      embed=embed
    )
  await s.close()
