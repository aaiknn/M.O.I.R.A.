#!/usr/bin/env python3

async def mindThoseArgs(moira, ctx, sessionUser, m):
  c = m.content
  chid = ctx.channel.id

  if sessionUser.role == 'admin':
    if 'reset' in c:
      if 'session' in c:
        if 'hard' in c:
          moira.tism.resetBusyState()
          moira.tism.resetSessionState()
          return 'DONE'
        elif 'soft' in c:
          moira.tism.setBusyState(chid, 'FALSE')
          moira.tism.setSessionState(chid, None)
