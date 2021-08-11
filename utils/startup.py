#!/usr/bin/env python3

from time import gmtime as timestamp

import logs.status as stat

async def logTests(noColour, webhook, situation):
  t             = timestamp()
  title         = stat.discord_webhook_log_moira_up_title
  messageStart  = stat.discord_webhook_log_moira_up_message.format(t)

  situation.logToTerm(noColour=noColour, messageStart=messageStart, title=title)

  if webhook['id'] and webhook['token']:
    try:
      await situation.logToDiscord(
        webhook,
        title=title,
        messageStart=messageStart)
    except Exception as e:
      situation.exceptions.append(f'Logging startup situation to Discord: {e}')
