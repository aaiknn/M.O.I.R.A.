#!/usr/bin/env python3

from logs import errors as ugh, warnings as warn
from sessions.exceptions import SubroutineException, MetaNotFoundException
from utils.api import EonetCall

async def dbSelftest(self, situation):
  try:
    selftest = await self.db.selfTest()
  except ConnectionAbortedError:
    self.tism.setSystemState('DB', 'DOWN')
    situation.errors.append(ugh.database_connection_aborted_error)
  except Exception as e:
    self.tism.setSystemState('DB', 'DOWN')
    situation.exceptions.append(f'{ugh.database_connection_error}: {e}')
  else:
    if not selftest:
      self.tism.setSystemState('DB', 'DOWN')
      situation.errors.append(ugh.database_connection_error_unknown)
      raise SubroutineException
    else:
      self.tism.setSystemState('DB', 'UP')

async def eonetSelftest(self, situation):
  s = EonetCall('categories')

  try:
    res = await s.sendCall()
  except Exception as e:
    self.tism.setSystemState('EONET', 'DOWN')
    situation.exceptions.append(f'{ugh.eonet_selftest_failed}: {e}')

  resObj = res.json()
  self.tism.setSystemState('EONET', 'UP')

  categories = []
  for category in resObj['categories']:
    categories.append(category['id'])

  if len(categories) == 0:
    situation.warnings.append(warn.eonet_categories_not_set)
    raise MetaNotFoundException(warn.eonet_categories_not_set)

  self.tism.setSystemState('EONET_categories', categories)
