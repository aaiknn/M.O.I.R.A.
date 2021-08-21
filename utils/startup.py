#!/usr/bin/env python3

from time import gmtime as timestamp

import logs.status as stat
import phrases.system as syx

async def logTests(webhook, situation):
  t             = timestamp()
  title         = stat.discord_webhook_log_moira_up_title
  messageStart  = stat.discord_webhook_log_moira_up_message.format(t)

  situation.logToTerm(messageStart=messageStart, title=title)

  if webhook['id'] and webhook['token']:
    try:
      await situation.logToDiscord(
        webhook,
        title=title,
        messageStart=messageStart)
    except Exception as e:
      situation.exceptions.append(f'{syx.logging_startup_to_discord}: {e}')
