#!/usr/bin/env python3

from asyncio import TimeoutError
from random import choice

from intentions.commands import confirm, reject
from phrases.default import decisionReceived, permissionDenied, permissionGranted, requestPermission as reqPerm, requestTimeout
from sessions.users import SessionAdmin, SessionUser

def checkForHighPermissions(self, userObj):
  check = False

  if isinstance(userObj, SessionAdmin):
    return True
  elif isinstance(userObj, SessionUser):
    return False
  else:
    for role in userObj.roles:
      if self.administrator in str(role):
        check = True
        break

  return check

async def requestPermission(self, ctx):
  await self.send(ctx, choice(reqPerm))

  def check(m):
    decision  = str.lower(m.content)
    check     = checkForHighPermissions(self, m.author)

    if check and any(word in decision for word in confirm):
      return True
    elif any(word in decision for word in reject):
      raise PermissionError
    else:
      return False

  try:
    perm = await self.wait_for('message', check=check, timeout=60.0)
  except TimeoutError:
    await self.send(ctx, choice(requestTimeout))
    return False
  except PermissionError:
    await self.send(ctx, f'{choice(decisionReceived)} {choice(permissionDenied)}')
    return False
  except Exception as e:
    raise e
  else:
    await self.send(ctx, f'{choice(decisionReceived)} {choice(permissionGranted)}')
    return perm
