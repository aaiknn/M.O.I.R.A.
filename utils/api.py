#!/usr/bin/env python3

from requests import get

class ApiCall:
  def __init__(self, **options):
    self.token    = options.get('token')

  async def apiSelftest(self):
    try:
      await self.sendCall()
    except Exception as e:
      raise e

  async def sendCall(self, **options):
    endpoint  = self.endpoint

    if options:
      endpoint += f'?'
      for option in options:
        endpoint += f'{option}='
        endpoint += str(options[option])
        endpoint += '&'
      uri = endpoint[:-1]
    else:
      uri = endpoint

    res = get(uri)
    if not res:
      raise ConnectionError

    return res

class EonetCall(ApiCall):
  def __init__(self, category='', **options):
    self.category = category
    self.options  = options

    self.endpoint = 'https://eonet.sci.gsfc.nasa.gov/api/v3/'

    if self.category:
      if self.category == 'categories':
        self.endpoint += 'categories'
      else:
        self.endpoint += f'categories/{self.category}'

    else:
      self.endpoint += 'events'

    super().__init__()

class ApiResponse:
  def __init__(self, _list, **options):
    self.options  = options
    self.list     = _list

class EonetResponse(ApiResponse):
  def __init__(self, res, **options):
    _dict             = res.json()
    _list             = []
    self.title        = _dict['title']
    self.description  = _dict['description']

    if _dict['events']:
      for event in _dict['events']:
        item = {
          'categories':   event['categories'],
          'closed':       event['closed'],
          'description':  event['description'],
          'geometry':     event['geometry'],
          'id':           event['id'],
          'link':         event['link'],
          'sources':      event['sources'],
          'title':        event['title']
        }
        _list.append(item)

    super().__init__(_list, **options)
