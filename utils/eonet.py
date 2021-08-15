#!/usr/bin/env python3

from discord import Embed
from random import choice
from re import sub
from typing import Tuple

from intentions.amounts import amounts
from intentions.qualification import eonetCallOptions as keywords
from phrases import terms
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

  if options.raw:
    cStr      = res._content.decode('utf-8')
    m         = cStr.replace('\t', '').replace('\n', '')
    await session.handler.send(ctx, m, code=True)
    return

  try:
    resObj    = EonetResponse(res)
    m         = formatMessage(resObj, limit)
  except Exception as e:
    sit.exceptions.append(e)

  else:
    if isinstance(m, Tuple):
      await session.handler.send(ctx, embed=f'{m[1]}')

      if m[0] == 'EMPTY':
        await session.handler.send(ctx, choice(emptyEonetResult))
      elif m[0] == 'LESS':
        await session.handler.send(ctx, choice(lessResults))

    else:
      await session.handler.send(ctx, '', embed=m)

def formatMessage(resObj, limit):
  title   = resObj.title if hasattr(resObj, 'title') else None
  desc    = resObj.description if hasattr(resObj, 'description') else None
  type    = resObj.type if hasattr(resObj, 'type') else None

  embed = Embed(
    title='',
    description=''
  )

  if title:
    embed.title += title
  elif type:
    embed.title += type
  else:
    embed.title += terms.eonet_response_fallback_title

  if desc:
    embed.description += desc

  if len(resObj.list) < 1:
    empt = ('EMPTY', embed)
    return empt

  for item in resObj.list:
    idate       = item['date'] if 'date' in item else None
    idesc       = item['description']
    isources    = item['sources']
    ititle      = item['title']

    fieldTitle  = ''
    fieldText   = ''

    if not item['closed']:
      fieldTitle += f':o:  [{terms.eonet_event_status_ongoing}] '
    else:
      fieldTitle += f':orange_circle:  [{terms.eonet_event_status_closed}] '

    if ititle:
      fieldTitle += ititle
    else:
      fieldTitle += terms.eonet_event_fallback_title

    if idate:
      fieldText += f'{idate}\n'

    if idesc:
      fieldText += f'{idesc}\n'

    if len(isources) > 0:
      fieldText += f'__{terms.eonet_event_sources}:__\n'
      for source in isources:
        sid   = source['id']
        surl  = source['url']

        fieldText += f'\t\t:small_blue_diamond: [{sid}]({surl})\n'

    if len(fieldText) == 0:
      fieldText += f'_{terms.eonet_event_no_details}_'

    embed.add_field(
      name=fieldTitle,
      value=fieldText
    )

  embed.set_footer(
    icon_url='https://pbs.twimg.com/profile_images/1321163587679784960/0ZxKlEKB_400x400.jpg',
    text=terms.eonet_response_footer_text
  )

  if len(resObj.list) < limit:
    less = ('LESS', embed)
    return less

  return embed

def mindThoseArgs(cats, userMessage):
  content   = sub(r'[^A-Za-z0-9 \-]+', ' ', userMessage.content)
  mList     = content.split(' ')
  limit     = 6
  cap       = 20

  options           = CallOptions()
  options.category  = None
  options.limit     = f'limit={limit}'
  options.raw       = False
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

    elif word == keywords['raw']:
      options.raw = True
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
