#!/usr/bin/env python3

from sessions.exceptions import UnreachableException
from utils.api import EonetCall, EonetResponse

async def handleEonet(handler, ctx, situation):
  sit       = situation

  try:
    s         = EonetCall('manmade')
    res       = await s.sendCall(limit=6, status='all')
    resObj    = EonetResponse(res)
    m         = formatMessage(resObj)

  except UnreachableException as f:
    sit.exceptions.append(f)

  except Exception as e:
    sit.exceptions.append(e)

  else:
    await handler.send(ctx, m)

def formatMessage(resObj):
  title   = resObj.title
  desc    = resObj.description

  m = f'```txt\n{title}'
  if desc:
    m += f'\n{desc}```\n'
  else:
    m += '```\n'

  for item in resObj.list:
    idesc      = item['description']
    isources   = item['sources']
    ititle     = item['title']

    if not item['closed']:
      m += ':o:  [ONGOING] '
    else:
      m += ':orange_circle:  [CLOSED] '

    m += f'**{ititle}**\n'

    if idesc:
      m += f'\t\t{idesc}\n'

    if len(isources) > 0:
      m += f'\t\tSources:\n'
      for source in isources:
        sid   = source['id']
        surl  = source['url']

        m += f'\t\t:small_blue_diamond: {sid}: {surl}\n'

    m += f'\n'

  return m
