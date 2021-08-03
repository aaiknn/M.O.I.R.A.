#!/usr/bin/env python3

from random import choice
from phrases.default import statementReceived

async def mindThoseArgs(self, ctx, sessionUser, m):
  c = m.content
  chid = ctx.channel.id

  if sessionUser.role == 'admin':
    if 'reset' in c:
      if 'session' in c:
        if 'hard' in c:
          self.tism.resetBusyState()
          self.tism.resetSessionState()
          self.send(ctx, choice(statementReceived))
          return 'DONE'
        elif 'soft' in c:
          self.tism.setBusyState(chid, 'FALSE')
          self.tism.setSessionState(chid, None)
          self.send(ctx, choice(statementReceived))
