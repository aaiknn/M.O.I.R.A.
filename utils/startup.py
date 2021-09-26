#!/usr/bin/env python3

from time import gmtime as timestamp

from logs import status, warnings as warn
import phrases.system as syx
from settings import prefs
from utils.selftests import dbSelftest, eonetSelftest, openAiSelftest

def readyUp(moira, globals):
  print(status.discord_moira_onready.format(moira))
  globals.status.append(status.discord_moira_onready.format(moira))

def setStates(moira, globals, loggers):
  moira.tism.setState('angryAt', {prefs.mPref_larry_name: prefs.mPref_larry_reason})
  moira.tism.resetBusyState()
  moira.tism.resetPromptHistory()
  moira.tism.resetSessionState()
  moira.tism.setState('promptQueue', {})

  if loggers.log_level > 0:
    globals.status.append(status.discord_moira_onready_onstatesready.format(moira))

async def runTests(moira, globals, loggers):
  try:
    await dbSelftest(moira, globals)
    await eonetSelftest(moira, globals)
    await openAiSelftest(moira, globals)

    if loggers.log_level > 0:
      globals.status.append(status.discord_moira_onready_onselftestsready.format(moira))

  except Exception as e:
    globals.exceptions.append(e)
    await globals.log(webhook=moira.webhook)
    globals.resetAll()
    globals.status.append(status.discord_moira_onready_ontestslogged.format(moira))
    globals.status.append(status.discord_moira_onready_onglobalsreset.format(moira))

def noteExceptions(moira, openai_api_token, globals, loggers):
  for meh in moira.db.errors:
    globals.errors.append(meh)

  if not moira.administrator and not moira.regularUser:
    globals.warnings.append(warn.moira_admin_and_user_not_set)
  elif not moira.administrator:
    globals.status.append(status.moira_admin_not_set)
  elif not moira.regularUser:
    globals.status.append(status.moira_user_not_set)

  if not openai_api_token:
    globals.warnings.append(warn.openai_token_not_set)

  if loggers.log_level > 0:
    globals.status.append(status.discord_moira_onready_onlogtests.format(moira))

async def logTests(webhook, situation):
  t             = timestamp()
  title         = status.discord_webhook_log_moira_up_title
  messageStart  = status.discord_webhook_log_moira_up_message.format(t)

  situation.logToTerm(messageStart=messageStart, title=title)

  if webhook['id'] and webhook['token']:
    try:
      await situation.logToDiscord(
        webhook,
        title=title,
        messageStart=messageStart)
    except Exception as e:
      situation.exceptions.append(f'{syx.logging_startup_to_discord}: {e}')
