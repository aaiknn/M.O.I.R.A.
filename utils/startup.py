#!/usr/bin/env python3

from aiohttp import ClientSession
from discord import Embed
from discord import AsyncWebhookAdapter
from time import gmtime as timestamp

import logs.status as status
from utils.general import getTermStyle
from utils.webhooks import DiscordHooks

async def logTests(noColour, scopedErrors, scopedWarnings, scopedStatus, webhook):
  boldred = getTermStyle('boldred', noColour)
  boldyellow = getTermStyle('boldyellow', noColour)
  bold = getTermStyle('bold', noColour)
  colourend = getTermStyle('colourend', noColour)

  for f in scopedErrors:
    print(f'\n{boldred}Error:{colourend} {f}')

  for huh in scopedWarnings:
    print(f'\n{boldyellow}Warning:{colourend} {huh}')

  for fact in scopedStatus:
    print(f'\n{bold}Status:{colourend} {fact}')

  if webhook['id'] and webhook['token']:
    await logStartupToDiscord(webhook, scopedErrors, scopedWarnings, scopedStatus)

async def logStartupToDiscord(webhook, scopedErrors, scopedWarnings, scopedStatus):
  s = ClientSession()
  async with s:
    t = timestamp()
    startUpMessage=status.discord_webhook_log_moira_up_message.format(t)
    colourCode=0x7a2faf
    if len(scopedWarnings) > 0:
      colourCode=0xfffa38
    if len(scopedErrors) > 0:
      colourCode=0xff4238

    if scopedErrors or scopedWarnings or scopedStatus:
      for error in scopedErrors:
        startUpMessage+=f'\n\n```diff\n- Error -\n```\n{error}'

      for warning in scopedWarnings:
        startUpMessage+=f'\n\n```fix\n- Warning -\n```\n{warning}'

      for fact in scopedStatus:
        startUpMessage+=f'\n\n```txt\n- Status -\n```\n{fact}'

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
