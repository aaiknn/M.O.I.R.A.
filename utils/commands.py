#!/usr/bin/env python3

from asyncio import TimeoutError
from random import choice

from intentions.commands import confirm, reject
from phrases.default import decisionReceived, onesidedBye, permissionDenied, permissionGranted, promptTimeout, requestPermission as reqPerm, requestTimeout
from utils.general import texting

def checkForPermission(self, user):
  check = False
  for role in user.roles:
    if self.administrator in str(role):
      check = True
      break
  return check

async def requestPermission(self, ctx):
  await texting(ctx)
  await ctx.send(choice(reqPerm))

  def check(m):
    check = checkForPermission(self, m.author)

    if check and any(word in m.content for word in confirm):
      return True
    elif any(word in m.content for word in reject):
      raise PermissionError
    else:
      return False

  try:
    perm = await self.wait_for('message', check=check, timeout=60.0)
  except TimeoutError:
    await texting(ctx)
    await ctx.send(choice(requestTimeout))
    return False
  except PermissionError:
    await texting(ctx)
    await ctx.send(f'{choice(decisionReceived)} {choice(permissionDenied)}')
    return False
  else:
    await texting(ctx)
    await ctx.send(f'{choice(decisionReceived)} {choice(permissionGranted)}')
    return perm

async def waitForAuthorisedPrompt(self, ctx, user):
  await ctx.send('What\'s your prompt?')
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
        await texting(ctx)
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

      break
