#!/usr/bin/env python3

from random import choice
from time import gmtime as timestamp

from phrases.default import stateResetHard, stateResetSoft, taskFailed, taskSuccessful
from phrases.default import sysOpComplete as complete, sysOpCompleteWithSideEffects as soClose
import phrases.system as syx

from sessions.exceptions import MoiraError
from utils.db import DBConnection
from utils.prompts import handleResponse, parsePrompt
from utils.selftests import dbSelftest, eonetSelftest

async def mindThoseArgs(self, ctx, sessionSituation, globalSession):
  sit         = sessionSituation
  sat         = globalSession
  c           = sit.userMessage.content
  chid        = sit.channelId
  chad        = ctx.author
  sessionUser = sit.sessionUser

  if sessionUser.role == 'admin':
    if c == f'{sit.handler.command_prefix}{sit.handler.nickname} ?':
      for prop, val in vars(sit.handler).items():
        await chad.send(f'moira.PROP: {prop}, moira.PROPVAL: {val}')
      await sat.logIfNecessary(
        title=syx.status_inquiry_title,
        webhook=sit.handler.webhook
      )

      return 'DONE'

    elif 'interactive' in c:
      await chad.send('DMSESSION')
      try:
        message = await self.wait_for('message', timeout=60.0)
      except Exception as e:
        sit.exeptions.append(e)
      else:
        response = await parsePrompt(sit.handler, ctx, message)
        await handleResponse(sit.handler, ctx, response)

      return 'DONE'

    elif 'attempt' in c:
      if 'db' in c:
        if 'connection' in c:
          taskName    = syx.attempt_db_connection
          localErrors = []

          try:
            await dbSelftest(self, localErrors)
          except Exception as e:
            exceptionMessage = f'{syx.task} {taskName}: {e}'
            localErrors.append(exceptionMessage)
          finally:
            for ugh in localErrors:
              self.db.errors.append(f'\n{ugh}')

          if self.tism.getSystemState('DB') == 'UP':
            await self.db.retrieveMeta(self)
            await self.send(ctx, choice(taskSuccessful).format(taskName), dm=True)
          elif self.tism.getSystemState('DB') == 'DOWN':
            await self.send(ctx, choice(taskFailed).format(taskName), dm=True)
          else:
            raise MoiraError(syx.subroutine_state_schrodinger.format('DB'))

          for f in localErrors:
            sit.errors.append(f)

          await sit.logIfNecessary(webhook=sit.handler.webhook)

          await self.send(ctx, choice(complete))
          return 'DONE'

      elif 'eonet' in c:
        if 'selftest' in c:
          taskName      = syx.attempt_eonet_selftest
          localErrors   = []
          localWarnings = []

          try:
            await eonetSelftest(self, localErrors, localWarnings)
          except Warning as w:
            warnMessage = f'{syx.task} {taskName}: {w}'
            localWarnings.append(warnMessage)
            sit.warnings.append(warnMessage)
          except Exception as e:
            exceptionMessage = f'{syx.task} {taskName}: {e}'
            localErrors.append(exceptionMessage)
            sit.exceptions.append(exceptionMessage)

          if self.tism.getSystemState('EONET') == 'UP':
            await self.send(ctx, choice(taskSuccessful).format(taskName), dm=True)
          elif self.tism.getSystemState('EONET') == 'DOWN':
            await self.send(ctx, f'{taskName}: {e}', dm=True)
          else:
            raise MoiraError(syx.subroutine_state_schrodinger.format('EONET'))

          await sit.logIfNecessary(webhook=sit.handler.webhook)

          await self.send(ctx, choice(complete))
          return 'DONE'

    if 'clear' in c:
      if 'db' in c:
        if 'errors' in c:
          self.db.errors = []
          return 'DONE'

    if 'load' in c:
      if 'state' in c:
        if 'last' in c:
          functionName  = 'DBConnection.restoreState()'
          taskName      = syx.load_state
          s             = DBConnection(self.db)

          try:
            await s.restoreState(self.tism.state)
          except Exception as e:
            exceptionMessage = f'{syx.function} {functionName}: {e}'
            s.errors.append(exceptionMessage)

          if len(s.errors) > 0:
            for ugh in s.errors:
              self.db.errors.append(ugh)
              sit.errors.append(ugh)
            await self.send(ctx, choice(taskFailed).format(taskName), dm=True)
          else:
            await self.send(ctx, choice(taskSuccessful).format(taskName), dm=True)

          await sit.logIfNecessary(webhook=sit.handler.webhook)

          await self.send(ctx, choice(complete))
          return 'DONE'

    elif 'reset' in c:
      if 'session' in c:
        if 'hard' in c:
          self.tism.resetBusyState()
          self.tism.resetSessionState()
          await self.send(ctx, choice(stateResetHard))
          return 'DONE'

        elif 'soft' in c:
          self.tism.setBusyState(chid, 'FALSE')
          self.tism.setSessionState(chid, None)
          await self.send(ctx, choice(stateResetSoft))

    elif 'shutdown' in c:
      if 'graceful' in c:
        functionName  = 'DBConnection.storeState():'
        t             = timestamp()
        s             = DBConnection(self.db)
        identifier    = str(f'{t.tm_year}-{t.tm_mon}-{t.tm_mday}-{t.tm_hour}-{t.tm_min}')

        try:
          newMeta = await s.storeState(self.tism.state, identifier)
        except Exception as e:
          exceptionMessage = f'{syx.function} {functionName}: {e}'
          s.errors.append(exceptionMessage)
          sit.errors.append(exceptionMessage)
          await self.send(ctx, choice(soClose))

        else:
          await self.send(ctx, choice(complete))
          self.db.state['meta']['HEAD'] = newMeta['HEAD']
          self.db.state['meta']['TAIL'] = newMeta['TAIL']

        finally:
          for ugh in s.errors:
            self.db.errors.append(ugh)

          await sit.logIfNecessary(webhook=sit.handler.webhook)

          return 'DONE'

    elif 'print' in c:
      if 'system' in c:
        if 'state' in c:
          dbErrors  = self.db.errors
          dbState   = str(self.db.state)
          eonetCats = str(self.tism.getSystemState('EONET_categories'))
          tism      = str(self.tism.state)
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

          await self.send(ctx, m, dm=True)
          await self.send(ctx, choice(complete))
          return 'DONE'

      elif 'db' in c:
        if 'errors' in c:
          dbErrors  = self.db.errors
          m         = ''

          if len(dbErrors) > 0:
            m += f'```txt\n- - moira.db.errors :```'
            for ugh in dbErrors:
              m += f'\n{ugh}'

          await self.send(ctx, m, dm=True)
          await self.send(ctx, choice(complete))
          return 'DONE'

        elif 'state' in c:
          dbState = str(self.db.state)
          m       = f'```txt\n- - moira.db.state :```\n'
          m += f'```txt\n{dbState}```\n'

          await self.send(ctx, m, dm=True)
          await self.send(ctx, choice(complete))
          return 'DONE'
