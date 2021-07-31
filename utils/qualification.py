#!/usr/bin/env python3

from asyncio import TimeoutError
from random import choice

from intentions.qualification import ai, cancelInput, eonet, shenanigans, sysinfo
from phrases.default import onesidedBye
from utils.general import texting

async def waitForQualificationInput(self, ctx, user):
  def check(m):
    return m.author == user

  try:
    topic = await self.wait_for('message', check=check, timeout=60.0)
  except TimeoutError:
      await texting(ctx, 2)
      await ctx.send(choice(onesidedBye))
  else:
    return topic

async def qualifyInput(self, topic):
  if any(word in topic for word in sysinfo):
    return 'SYSINFO'

  elif any(word in topic for word in ai):
    if self.tism.getState('AI') == 'UP':
      self.tism.setState('busyWith', 'AI')
    else:
      raise ModuleNotFoundError

  elif any(word in topic for word in eonet):
    if self.tism.getState('EONET') == 'UP':
      self.tism.setState('busyWith', 'EONET')
    else:
      raise ModuleNotFoundError

  elif any(word in topic for word in shenanigans):
    raise TypeError

  elif any(word in topic for word in cancelInput):
    raise InterruptedError

  else:
    raise NotImplementedError
