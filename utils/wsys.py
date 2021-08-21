#!/usr/bin/env python3

from random import choice
from typing import List

from data.wsys import _dict as endpoints
from phrases.default import beforeResearch, complete
import phrases.system as syx
from sessions.exceptions import UnreachableException
from utils.api import ApiCall

async def handleWsys(ctx, moiraSession, situation):
  session = moiraSession
  sit     = situation

  await session.handler.send(ctx, choice(beforeResearch))

  for item in endpoints.items():
    name      = item[0]
    endpoint  = item[1]

    try:
      s         = ApiCall(endpoint=endpoint)
      res       = await s.sendCall()
    except UnreachableException as f:
      sit.warnings.append(f'{name}: {f}')
    except Exception as e:
      sit.exceptions.append(f'{name}: {e}')

    else:
      m = res.json()
      if isinstance(m, List):
        for item in m:
          for entry in item.items():
            print(entry)
            break
          break

      else:
        for item in m.items():
          print(item)
          break

  await session.handler.send(ctx, choice(complete))
  await sit.logIfNecessary(
    title=f'{syx.x_situation_log.format(syx.wsys_call)}',
    webhook=sit.handler.webhook
  )
  sit.resetAll()
