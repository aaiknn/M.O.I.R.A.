#!/usr/bin/env python3

from random import choice
from time import gmtime as timestamp

from discord import webhook

from logs import status
from phrases.default import stateResetHard, stateResetSoft, taskFailed, taskSuccessful
from phrases.default import sysOpComplete as complete, sysOpCompleteWithSideEffects as soClose
import phrases.system as syx

from sessions.exceptions import MoiraError
from utils.db import DBConnection
from utils.prompts import handleResponse, parsePrompt
from utils.selftests import dbSelftest, eonetSelftest

async def mindThoseArgs(moira, ctx, sessionSituation, globalSession, loggers):
  sit         = sessionSituation
  sat         = globalSession
  c           = sit.userMessage.content
  chid        = sit.channelId
  chad        = ctx.author
  sessionUser = sit.sessionUser

  if loggers.log_level > 0:
    globalSession.status.appendMessage(status.discord_moira_admin_session_started.format(moira, ctx.author, chid))

  if sessionUser.role == 'admin':
    if c == f'{sit.handler.command_prefix}{sit.handler.nickname} ?':
      for prop, val in vars(sit.handler).items():
        await chad.send(f'moira.PROP: {prop}, moira.PROPVAL: {val}')
      await sat.logIfNecessary(
        title=syx.status_inquiry_title,
        webhook=sit.handler.webhook
      )

      if loggers.log_level > 0:
        globalSession.status.appendMessage(status.discord_moira_admin_session_ended.format(moira, ctx.author, chid))
      return 'DONE'

    elif 'interactive' in c:
      if loggers.log_level > 0:
        globalSession.status.appendMessage(status.discord_moira_admin_dm_session_initialised.format(moira, ctx.author, chid))
      await chad.send('DMSESSION')

      try:
        message = await moira.wait_for('message', timeout=60.0)
      except Exception as e:
        sit.exeptions.appendMessage(e)
      else:
        response = await parsePrompt(sit.handler, ctx, message)
        await handleResponse(sit.handler, ctx, response)

      if loggers.log_level > 0:
        globalSession.status.appendMessage(status.discord_moira_admin_session_ended.format(moira, ctx.author, chid))
      return 'DONE'

    elif 'attempt' in c:
      if 'db' in c:
        if 'connection' in c:
          taskName    = syx.attempt_db_connection
          localErrors = []

        if loggers.log_level > 0:
          globalSession.status.appendMessage(status.discord_moira_admin_dbc_attempt.format(moira, ctx.author, chid))

          try:
            await dbSelftest(moira, localErrors)

          except Exception as e:
            exceptionMessage = f'{syx.task} {taskName}: {e}'
            localErrors.append(exceptionMessage)
            if loggers.log_level > 0:
              globalSession.status.appendMessage(status.discord_moira_admin_dbc_failed.format(moira, chid))

          finally:
            for ugh in localErrors:
              moira.db.errors.append(f'\n{ugh}')

          if moira.tism.getSystemState('DB') == 'UP':
            await moira.db.retrieveMeta(moira)
            await moira.send(ctx, choice(taskSuccessful).format(taskName), dm=True)
            if loggers.log_level > 0:
              globalSession.status.appendMessage(status.discord_moira_admin_dbc_success.format(moira, chid))

          elif moira.tism.getSystemState('DB') == 'DOWN':
            await moira.send(ctx, choice(taskFailed).format(taskName), dm=True)
          else:
            raise MoiraError(syx.subroutine_state_schrodinger.format('DB'))

          for f in localErrors:
            sit.errors.appendMessage(f)

          await sit.logIfNecessary(webhook=sit.handler.webhook)

          await moira.send(ctx, choice(complete))
          if loggers.log_level > 0:
            globalSession.status.appendMessage(status.discord_moira_admin_session_ended.format(moira, ctx.author, chid))
          return 'DONE'

      elif 'eonet' in c:
        if 'selftest' in c:
          taskName      = syx.attempt_eonet_selftest
          localErrors   = []
          localWarnings = []

        if loggers.log_level > 0:
          globalSession.status.appendMessage(status.discord_moira_admin_eonet_attempt.format(moira, ctx.author, chid))

          try:
            await eonetSelftest(moira, localErrors, localWarnings)

          except Warning as w:
            warnMessage = f'{syx.task} {taskName}: {w}'
            localWarnings.append(warnMessage)
            sit.warnings.appendMessage(warnMessage)

          except Exception as e:
            exceptionMessage = f'{syx.task} {taskName}: {e}'
            localErrors.append(exceptionMessage)
            sit.exceptions.appendMessage(exceptionMessage)

          if moira.tism.getSystemState('EONET') == 'UP':
            await moira.send(ctx, choice(taskSuccessful).format(taskName), dm=True)
            if loggers.log_level > 0:
              globalSession.status.appendMessage(status.discord_moira_admin_eonet_attempt_success.format(moira, chid))

          elif moira.tism.getSystemState('EONET') == 'DOWN':
            await moira.send(ctx, f'{taskName}: {e}', dm=True)
            if loggers.log_level > 0:
              globalSession.status.appendMessage(status.discord_moira_admin_eonet_attempt_failed.format(moira, chid))

          else:
            raise MoiraError(syx.subroutine_state_schrodinger.format('EONET'))

          await sit.logIfNecessary(webhook=sit.handler.webhook)

          await moira.send(ctx, choice(complete))
          if loggers.log_level > 0:
            globalSession.status.appendMessage(status.discord_moira_admin_session_ended.format(moira, ctx.author, chid))
          return 'DONE'

    if 'clear' in c:
      if 'db' in c:
        if 'errors' in c:
          moira.db.errors = []
          if loggers.log_level > 0:
            globalSession.status.appendMessage(status.discord_moira_admin_db_errors_cleared.format(moira, ctx.author, chid))
            globalSession.status.appendMessage(status.discord_moira_admin_session_ended.format(moira, ctx.author, chid))
          return 'DONE'

    if 'load' in c:
      if 'state' in c:
        if 'last' in c:
          functionName  = 'DBConnection.restoreState()'
          taskName      = syx.load_state
          s             = DBConnection(moira.db)

          try:
            await s.restoreState(moira.tism.state)

          except Exception as e:
            exceptionMessage = f'{syx.function} {functionName}: {e}'
            s.errors.append(exceptionMessage)
            if loggers.log_level > 0:
              globalSession.status.appendMessage(status.discord_moira_admin_state_load_failed.format(moira, ctx.author, chid))

          if len(s.errors) > 0:
            for ugh in s.errors:
              moira.db.errors.append(ugh)
              sit.errors.appendMessage(ugh)
            await moira.send(ctx, choice(taskFailed).format(taskName), dm=True)

          else:
            await moira.send(ctx, choice(taskSuccessful).format(taskName), dm=True)
            if loggers.log_level > 0:
              globalSession.status.appendMessage(status.discord_moira_admin_state_load_success.format(moira, ctx.author, chid))

          await sit.logIfNecessary(webhook=sit.handler.webhook)

          await moira.send(ctx, choice(complete))
          if loggers.log_level > 0:
            globalSession.status.appendMessage(status.discord_moira_admin_session_ended.format(moira, ctx.author, chid))

          return 'DONE'

    elif 'reset' in c:
      if 'session' in c:
        if 'hard' in c:
          moira.tism.resetBusyState()
          moira.tism.resetSessionState()
          await moira.send(ctx, choice(stateResetHard))

          if loggers.log_level > 0:
            globalSession.status.appendMessage(status.discord_moira_admin_session_reset_hard.format(moira, ctx.author, chid))
            globalSession.status.appendMessage(status.discord_moira_admin_session_ended.format(moira, ctx.author, chid))

          return 'DONE'

        elif 'soft' in c:
          moira.tism.setBusyState(chid, 'FALSE')
          moira.tism.setSessionState(chid, None)
          await moira.send(ctx, choice(stateResetSoft))

          if loggers.log_level > 0:
            globalSession.status.appendMessage(status.discord_moira_admin_session_reset_soft.format(moira, ctx.author, chid))

    elif 'shutdown' in c:
      if 'graceful' in c:
        functionName  = 'DBConnection.storeState():'
        t             = timestamp()
        s             = DBConnection(moira.db)
        identifier    = str(f'{t.tm_year}-{t.tm_mon}-{t.tm_mday}-{t.tm_hour}-{t.tm_min}')

        if loggers.log_level > 0:
          globalSession.status.appendMessage(status.discord_moira_admin_gs_initiated.format(moira, ctx.author, chid))

        try:
          newMeta = await s.storeState(moira.tism.state, identifier)
        except Exception as e:
          exceptionMessage = f'{syx.function} {functionName}: {e}'
          s.errors.append(exceptionMessage)
          sit.errors.append(exceptionMessage)
          await moira.send(ctx, choice(soClose))
          if loggers.log_level > 0:
            globalSession.status.appendMessage(status.discord_moira_admin_gs_failed.format(moira, chid))

        else:
          await moira.send(ctx, choice(complete))
          moira.db.state['meta']['HEAD'] = newMeta['HEAD']
          moira.db.state['meta']['TAIL'] = newMeta['TAIL']

          if loggers.log_level > 0:
            globalSession.status.appendMessage(status.discord_moira_admin_gs_success.format(moira, chid))

        finally:
          for ugh in s.errors:
            moira.db.errors.append(ugh)

          await sit.logIfNecessary(webhook=sit.handler.webhook)

          if loggers.log_level > 0:
            globalSession.status.appendMessage(status.discord_moira_admin_session_ended.format(moira, ctx.author, chid))
          return 'DONE'

    elif 'print' in c:
      if 'system' in c:
        if 'state' in c:
          dbErrors  = moira.db.errors
          dbState   = str(moira.db.state)
          eonetCats = str(moira.tism.getSystemState('EONET_categories'))
          tism      = str(moira.tism.state)
          m         = ''

          if len(dbErrors) > 0:
            m += f'```txt\n- - moira.db.errors :```'
            for ugh in dbErrors:
              m += f'\n{ugh}'

          m += f'```txt\n- - moira.db.state :```\n'
          m += f'```txt\n{dbState}```\n'

          m += f'```txt\n- - moira.tism.state :```\n'
          m += f'{tism}\n\n'

          m += f'```txt\n- - EONET_categories :```\n'
          m += f'```txt\n{eonetCats}```\n'

          await moira.send(ctx, m, dm=True)
          await moira.send(ctx, choice(complete))
          if loggers.log_level > 0:
            globalSession.status.appendMessage(status.discord_moira_admin_state_printed.format(moira, ctx.author))
            globalSession.status.appendMessage(status.discord_moira_admin_session_ended.format(moira, ctx.author, chid))

          return 'DONE'

      elif 'db' in c:
        if 'errors' in c:
          dbErrors  = moira.db.errors
          m         = ''

          if len(dbErrors) > 0:
            m += f'```txt\n- - moira.db.errors :```'
            for ugh in dbErrors:
              m += f'\n{ugh}'

          await moira.send(ctx, m, dm=True)
          await moira.send(ctx, choice(complete))
          if loggers.log_level > 0:
            globalSession.status.appendMessage(status.discord_moira_admin_db_errors_printed.format(moira, ctx.author))
            globalSession.status.appendMessage(status.discord_moira_admin_session_ended.format(moira, ctx.author, chid))
          return 'DONE'

        elif 'state' in c:
          dbState = str(moira.db.state)
          m       = f'```txt\n- - moira.db.state :```\n'
          m += f'```txt\n{dbState}```\n'

          await moira.send(ctx, m, dm=True)
          await moira.send(ctx, choice(complete))
          if loggers.log_level > 0:
            globalSession.status.appendMessage(status.discord_moira_admin_db_state_printed.format(moira, ctx.author))
            globalSession.status.appendMessage(status.discord_moira_admin_session_ended.format(moira, ctx.author, chid))
          return 'DONE'

  if loggers.log_level > 0:
    globalSession.status.appendMessage(status.discord_moira_admin_session_ended.format(moira, ctx.author, chid))
    globalSession.logToTerm(title=syx.admin_session_log, webhook=moira.webhook)
    globalSession.resetAll()
