#!/usr/bin/env python3

from asyncio import TimeoutError
from random import choice

from phrases.default import onesidedBye, promptTimeout
from utils.general import texting

def checkForPermission(self, user):
  check = False
  for role in user.roles:
    if self.permission_role in str(role):
      check = True
      break
  return check

async def requestPermission(self, ctx):
  await ctx.send('Requesting permission to do so.')

  def check(m):
    check = checkForPermission(self, m.author)
    if check and 'yes' in m.content:
      return True
    else:
      return False

  try:
    perm = await self.wait_for('message', check=check, timeout=60.0)
  except TimeoutError:
    await ctx.send('Request timeout.')
    return False
  else:
    return perm

async def waitingForInput(self, ctx, user):
  def check(m):
    return m.author == user

  for i in range(0, self.patience):
    try:
      prompt = await self.wait_for('message', check=check, timeout=60.0)
    except TimeoutError:
      if i == (self.patience - 1):
        await texting(ctx, 2)
        await ctx.send(choice(onesidedBye))
        break
      else:
        await texting(ctx, 1)
        await ctx.send(choice(promptTimeout))
        continue
    else:
      perm = checkForPermission(self, ctx.author)
      if perm:
        return prompt
      else:
        req = await requestPermission(self, ctx)
        if req:
          return prompt