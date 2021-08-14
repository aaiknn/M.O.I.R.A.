#!/usr/bin/env python3

from random import choice
from re import sub
from typing import Tuple

from intentions.amounts import amounts
from intentions.qualification import eonetCallOptions as keywords
from phrases.default import beforeResearch, emptyEonetResult, lessResults
from sessions.exceptions import UnreachableException
from utils.api import EonetCall, EonetResponse, CallOptions

async def handleEonet(ctx, moiraSession, situation):
  session   = moiraSession
  eventCats = session.handler.tism.getSystemState('EONET_categories')
  options   = mindThoseArgs(eventCats, session.userMessage)
  sit       = situation

  await session.handler.send(ctx, choice(beforeResearch))

  try:
    s         = EonetCall(options.category)
    res       = await s.sendCall(options.limit, options.status)
  except UnreachableException as f:
    sit.exceptions.append(f)
  except Exception as e:
    sit.exceptions.append(e)

  limit       = options.limit.split('=')
  limit       = int(limit[1])

  try:
    resObj    = EonetResponse(res)
    m         = formatMessage(resObj, limit)
  except Exception as e:
    sit.exceptions.append(e)
  else:
    if isinstance(m, Tuple):
      await session.handler.send(ctx, f'{m[1]}')

      if m[0] == 'EMPTY':
        await session.handler.send(ctx, choice(emptyEonetResult))
      elif m[0] == 'LESS':
        await session.handler.send(ctx, choice(lessResults))

    else:
      await session.handler.send(ctx, m)

def formatMessage(resObj, limit):
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

  if len(resObj.list) < 1:
    empt = ('EMPTY', m)
    return empt

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
      m += f'\t\t{idate}\n'

    if idesc:
      m += f'\t\t{idesc}\n'

    if len(isources) > 0:
      m += f'\t\tSources:\n'
      for source in isources:
        sid   = source['id']
        surl  = source['url']

        m += f'\t\t:small_blue_diamond: {sid}: <{surl}>\n'

  if len(resObj.list) < limit:
    less = ('LESS', m)
    return less

  return m

def mindThoseArgs(cats, userMessage):
  content   = sub(r'[^A-Za-z0-9 \-]+', ' ', userMessage.content)
  mList     = content.split(' ')
  limit     = 6
  cap       = 20

  options           = CallOptions()
  options.category  = None
  options.limit     = f'limit={limit}'
  options.status    = 'status=all'

  for i in range(1, len(cats)):
    j = i - 1
    word = cats.pop(j).lower()
    cats.insert(j, word)

  for word in mList:
    word = word.lower()

    if word == keywords['uncap']:
      cap   = None
      continue

    elif word in cats:
      options.category = word
      continue

    elif word in keywords['status']:
      s = keywords['status'][word]
      options.status  = f'status={s}'
      continue

    elif word in amounts:
      limit = amounts[word]
      continue

    else:
      try:
        _int = int(word)
      except ValueError:
        pass
      else:
        limit = _int

  if limit and cap and limit > cap:
    options.limit = f'limit={cap}'
  elif limit:
    options.limit = f'limit={limit}'

  return options
