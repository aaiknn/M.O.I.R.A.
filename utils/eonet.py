#!/usr/bin/env python3

from sessions.exceptions import UnreachableException
from utils.api import EonetCall, EonetResponse, CallOptions

async def handleEonet(ctx, moiraSession, situation):
  session   = moiraSession
  eventCats = session.handler.tism.getSystemState('EONET_categories')

  options   = mindThoseArgs(eventCats, session.userMessage)
  sit       = situation

  try:
    s         = EonetCall(options.category)
    res       = await s.sendCall(limit=6, status='all')
  except UnreachableException as f:
    sit.exceptions.append(f)
  except Exception as e:
    sit.exceptions.append(e)

  try:
    resObj    = EonetResponse(res)
    m         = formatMessage(resObj)
  except Exception as e:
    sit.exceptions.append(e)
  else:
    await session.handler.send(ctx, m)

def formatMessage(resObj):
  title   = resObj.title if hasattr(resObj, 'title') else None
  desc    = resObj.description if hasattr(resObj, 'description') else None
  type    = resObj.type if hasattr(resObj, 'type') else None

  if title or desc or type:
    m = '```txt'
  else:
    m = ''

  if title:
   m += f'\n{title}\n'

  if desc:
    m += f'\n{desc}```\n'
  elif type:
    m += f'\n{type}```\n'
  elif title:
    m += '```\n'

  for item in resObj.list:
    idate       = item['date'] if 'date' in item else None
    idesc       = item['description']
    isources    = item['sources']
    ititle      = item['title']

    if not item['closed']:
      m += ':o:  [ONGOING] '
    else:
      m += ':orange_circle:  [CLOSED] '

    if ititle:
      m += f'**{ititle}**\n'
    else:
      m += f'**Natural Event**\n'

    if idate:
      m += f'\t\t{idate}\n\n'

    if idesc:
      m += f'\t\t{idesc}\n'

    if len(isources) > 0:
      m += f'\t\tSources:\n'
      for source in isources:
        sid   = source['id']
        surl  = source['url']

        m += f'\t\t:small_blue_diamond: {sid}: <{surl}>\n'

  return m

def mindThoseArgs(cats, userMessage):
  options   = CallOptions()
  mList     = userMessage.content.split(' ')

  options.category = None

  for i in range(1, len(cats)):
    j = i - 1
    word = cats.pop(j).lower()
    cats.insert(j, word)

  for word in mList:
    word = word.lower()

    if word in cats:
      options.category = word

  return options
