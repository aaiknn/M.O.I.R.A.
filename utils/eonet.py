#!/usr/bin/env python3

from discord import Embed
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
    embed.title += 'Earth Observatory Natural Event Tracker (EONET)'

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
      fieldTitle += ':o:  [ONGOING] '
    else:
      fieldTitle += ':orange_circle:  [CLOSED] '

    if ititle:
      fieldTitle += ititle
    else:
      fieldTitle += 'Natural Event'

    if idate:
      fieldText += f'{idate}\n'

    if idesc:
      fieldText += f'{idesc}\n'

    if len(isources) > 0:
      fieldText += '__Sources:__\n'
      for source in isources:
        sid   = source['id']
        surl  = source['url']

        fieldText += f'\t\t:small_blue_diamond: [{sid}]({surl})\n'

    if len(fieldText) == 0:
      fieldText += '_No available details_'

    embed.add_field(
      name=fieldTitle,
      value=fieldText
    )

  embed.set_footer(
    icon_url='https://pbs.twimg.com/profile_images/1321163587679784960/0ZxKlEKB_400x400.jpg',
    text='EONET is the Earth Observatory Natural Event Tracker. EONET is a repository of metadata about natural events. EONET is accessible via web services. EONET will drive your natural event application. EONET metadata is for visualization and general information purposes only and should not be construed as \'official\' with regards to spatial or temporal extent.'
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
