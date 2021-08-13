#!/usr/bin/env python3

from requests import get
from sessions.exceptions import UnreachableException

class ApiCall:
  def __init__(self, **options):
    self.token    = options.get('token')

  async def apiSelftest(self):
    try:
      await self.sendCall()
    except Exception as e:
      raise UnreachableException

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
      raise UnreachableException

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
      self.endpoint += 'events/geojson'

    super().__init__()

class ApiResponse:
  def __init__(self, _list, **options):
    self.options  = options
    self.list     = _list

class EonetResponse(ApiResponse):
  def __init__(self, res, **options):
    _dict               = res.json()
    _list               = []
    self.title          = _dict['title'] if 'title' in _dict else None
    self.description    = _dict['description'] if 'description' in _dict else None
    self.type           = _dict['type'] if 'type' in _dict  else None

    # Events API
    if 'events' in _dict:
      for event in _dict['events']:
        eventItem = {
          'categories':     event['categories'],
          'closed':         event['closed'],
          'description':    event['description'],
          'geometry':       event['geometry'],
          'id':             event['id'],
          'link':           event['link'],
          'sources':        event['sources'],
          'title':          event['title']
        }
        _list.append(eventItem)

    # GeoJSON API
    if 'features' in _dict:
      for feat in _dict['features']:
        eventItem = {
          'geometry':       feat['geometry'],
          'type':           feat['type']
        }

        if 'properties' in feat:
          eventItem['categories']   = feat['properties']['categories']
          eventItem['closed']       = feat['properties']['closed']
          eventItem['date']         = feat['properties']['date'] if 'date' in feat['properties'] else None
          eventItem['description']  = feat['properties']['description']
          eventItem['id']           = feat['properties']['id']
          eventItem['link']         = feat['properties']['link']
          eventItem['sources']      = feat['properties']['sources']
          eventItem['title']        = feat['properties']['title']

        _list.append(eventItem)

    super().__init__(_list, **options)

class CallOptions:
  def __init__(self, **options):
    self.options = options
