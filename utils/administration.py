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
    if 'reset' in c:
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
          docId = await s.storeState(self.tism.state, identifier)
        except Exception as e:
          await self.send(ctx, choice(soClose))
        else:
          await self.send(ctx, choice(complete))
          return 'DONE'
    elif 'print' in c:
      if 'system' in c:
        if 'state' in c:
          dbErrors = self.db.errors
          tism = self.tism.state
          m = ''

          if len(dbErrors) > 0:
            m += f'```txt\n- - moira.db.errors :```\n'
            for ugh in dbErrors:
              m += f'\n{ugh}'

          m += f'```txt\n- - moira.tism.state :```\n'
          m += f'\n{tism}'

          await self.send(ctx, m, dm=True)
          await self.send(ctx, choice(complete))
          return 'DONE'
      elif 'db' in c:
        if 'errors' in c:
          dbErrors = self.db.errors
          m = ''

          if len(dbErrors) > 0:
            m += f'```txt\n- - moira.db.errors :```\n'
            for ugh in dbErrors:
              m += f'\n{ugh}'

          await self.send(ctx, m, dm=True)
