#!/usr/bin/env python3

from random import choice

from logs import status
from phrases.default import basicScriptFail
import phrases.system as syx

async def handleCommandError(moira, ctx, globals, error, loggers):
  globals.status.append(status.discord_moira_onevent_oncommanderror.format(moira))
  errorMessage = syx.error_on_command.format(error)
  globals.errors.appendMessage(errorMessage)
  await globals.log(webhook=moira.webhook)

  if loggers.log_level > 0:
    globals.status.appendMessage(status.discord_moira_onready_onglobalslogged.format(moira))

  globals.resetAll()

  if loggers.log_level > 0:
    globals.status.appendMessage(status.discord_moira_onready_onglobalsreset.format(moira))

  await moira.send(ctx, f"{choice(basicScriptFail)} `{error}`.")

  if loggers.log_level > 0:
    globals.status.appendMessage(status.discord_moira_onevent_oncommanderror_stop.format(moira))
