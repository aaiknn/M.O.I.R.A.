#!/usr/bin/env python3

from random import choice
from phrases.default import stateResetHard, stateResetSoft

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
