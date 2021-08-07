#!/usr/bin/env python3

from random import choice
from time import gmtime as timestamp
from utils.db import DBConnection

from phrases.default import stateResetHard, stateResetSoft
from phrases.default import sysOpComplete as complete, sysOpCompleteWithSideEffects as soClose

async def mindThoseArgs(self, ctx, sessionUser, m):
  c = m.content
  chid = ctx.channel.id

  if sessionUser.role == 'admin':
    if 'clear' in c:
      if 'db' in c:
        if 'errors' in c:
          self.db.errors = []
          return 'DONE'

    if 'load' in c:
      if 'state' in c:
        if 'last' in c:
          s = DBConnection(self.db)
          try:
            await s.restoreState(self.tism.state)
          except Exception as e:
            s.errors.append(f'DBConnection.restoreState(): {e}')
          finally:
            if len(s.errors) > 0:
              for ugh in s.errors:
                self.db.errors.append(ugh)
              await self.send(ctx, choice(soClose))
            else:
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
        t = timestamp()
        s = DBConnection(self.db)
        identifier = str(f'{t.tm_year}-{t.tm_mon}-{t.tm_mday}-{t.tm_hour}-{t.tm_min}')
        try:
          newMeta = await s.storeState(self.tism.state, identifier)
        except Exception as e:
          s.errors.append(f'DBConnection.storeState(): {e}')
          await self.send(ctx, choice(soClose))
        else:
          await self.send(ctx, choice(complete))
          self.db.state['meta']['HEAD'] = newMeta['HEAD']
          self.db.state['meta']['TAIL'] = newMeta['TAIL']
        finally:
          for ugh in s.errors:
            self.db.errors.append(ugh)
          return 'DONE'

    elif 'print' in c:
      if 'system' in c:
        if 'state' in c:
          dbErrors  = self.db.errors
          dbState   = str(self.db.state)
          tism      = str(self.tism.state)
          m         = ''

          if len(dbErrors) > 0:
            m += f'```txt\n- - moira.db.errors :```'
            for ugh in dbErrors:
              m += f'\n{ugh}'

          m += f'```txt\n- - moira.db.state :```\n'
          m += f'```txt\n{dbState}```\n'

          m += f'```txt\n- - moira.tism.state :```\n'
          m += f'{tism}'

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
