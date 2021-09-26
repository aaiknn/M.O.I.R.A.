#!/usr/bin/env python3

from random import choice
from time import gmtime, strftime

from data.wsys import _dict as endpoints
from phrases.default import beforeWsys, complete
from phrases import terms, system as syx
from sessions.exceptions import UnreachableException
from utils.api import ApiCall
from utils.reports import Report

async def handleWsys(ctx, moiraSession, situation, paths):
  data      = []
  session   = moiraSession
  sit       = situation
  timestamp = strftime(terms.wsys_report_timestamp_format, gmtime())

  await session.handler.send(ctx, choice(beforeWsys))

  data.append({
    'title':  terms.wsys_report_title,
    'date':   timestamp,
    'apis':   []
  })

  for item in endpoints.items():
    name      = item[0]
    details   = item[1]

    endpoint      = details['endpoint']
    responseType  = details['responseType']
    subtitle      = details['subtitle']
    title         = details['title']

    try:
      s         = ApiCall(endpoint=endpoint)
      res       = await s.sendCall()
    except UnreachableException as f:
      sit.warnings.appendMessage(f'{name}: {f}')
    except Exception as e:
      sit.exceptions.appendMessage(f'{name}: {e}')
    else:
      json      = res.json()

      try:
        parseWsysResponse(responseType, json, title=title, subtitle=subtitle, data=data)
        data[0]['apis'].append(title)
      except Exception as e:
        raise Exception(e)

  try:
    report = Report(
      fileName='report.pdf',
      path=paths['reports']
    )
    report.create()
    report.write(data=data)
    await report.send(ctx)

  except Exception as e:
    raise Exception(e)

  else:
    await session.handler.send(ctx, choice(complete))

  await sit.logIfNecessary(
    title=f'{syx.x_situation_log.format(syx.wsys_call)}',
    webhook=sit.handler.webhook
  )
  sit.resetAll()

def parseWsysResponse(responseType, json, itemData='', **options):
  data      = options.get('data')
  itemData  = itemData
  response  = json
  subtitle  = options.get('subtitle')
  title     = options.get('title')

  data.append((title, 'Heading2'))
  data.append((subtitle, 'Heading3'))

  if responseType == 'PGO':
    for item in response:
      itemData += item['water']['longname']
      itemData += ' at '
      itemData += item['shortname']
      if 'km' in item:
        itemData += ' ('
        itemData += str(item['km'])
        itemData += ')'
      itemData += ': '
      itemData += str(item['number'])
      itemData += '\n'

    data.append(itemData)

  elif responseType == 'UKF':
    for item in response['items']:
      headline = item['severity']
      headline += ' - '
      headline += item['floodArea']['county']
      headline += '. '
      headline += item['floodArea']['riverOrSea']

      itemData += item['eaAreaName']
      itemData += ', '
      itemData += item['description']
      itemData += '\n\n'
      itemData += item['message']
      itemData += '\n\n'

      data.append((headline, 'Heading4'))
      data.append(itemData)

      headline = ''
      itemData = ''
