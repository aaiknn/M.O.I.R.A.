#!/usr/bin/env python3

from asyncio import TimeoutError
from random import choice

from intentions.qualification import ai, cancelInput, eonet, shenanigans, sysinfo
from phrases.default import onesidedBye
from sessions.exceptions import MoiraTypeError

async def waitForQualificationInput(self, ctx):
  def check(m):
    return m.author == ctx.author

  try:
    message = await self.wait_for('message', check=check, timeout=60.0)
  except TimeoutError:
    await self.send(ctx, choice(onesidedBye), 2)
  else:
    return message

async def qualifyInput(self, chid, message):
  message = str.lower(message.content)

  if any(word in message for word in sysinfo):
    return 'SYSINFO'

  elif any(word in message for word in ai):
    if self.tism.getSystemState('AI') == 'UP':
      self.tism.addToSessionState(chid, 'active_subroutine', 'AI')
    else:
      raise ModuleNotFoundError

  elif any(word in message for word in eonet):
    if self.tism.getSystemState('EONET') == 'UP':
      self.tism.addToSessionState(chid, 'active_subroutine', 'EONET')
    else:
      raise ModuleNotFoundError

  elif any(word in message for word in shenanigans):
    raise MoiraTypeError

  elif any(word in message for word in cancelInput):
    raise InterruptedError

  else:
    raise NotImplementedError
