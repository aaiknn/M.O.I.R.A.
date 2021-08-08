#!/usr/bin/env python3

from logs import errors as ugh, warnings as warn
from utils.api import EonetCall

async def dbSelftest(self, scopedErrors):
  try:
    selftest = await self.db.selfTest()
  except ConnectionAbortedError:
    self.tism.setSystemState('DB', 'DOWN')
    scopedErrors.append(ugh.database_connection_aborted_error)
  except Exception as e:
    self.tism.setSystemState('DB', 'DOWN')
    scopedErrors.append(f'{ugh.database_connection_error}: {e}')
  else:
    if not selftest:
      self.tism.setSystemState('DB', 'DOWN')
      scopedErrors.append(ugh.database_connection_error_unknown)
    else:
      self.tism.setSystemState('DB', 'UP')

async def eonetSelftest(self, scopedErrors, scopedWarnings):
  s = EonetCall('categories')

  try:
    res = await s.sendCall()
  except Exception as e:
    self.tism.setSystemState('EONET', 'DOWN')
    scopedErrors.append(f'{ugh.eonet_selftest_failed}: {e}')
    raise e

  resObj = res.json()
  self.tism.setSystemState('EONET', 'UP')

  categories = []
  for category in resObj['categories']:
    categories.append(category['id'])

  if len(categories) == 0:
    scopedWarnings.append(warn.eonet_categories_not_set)
    raise Warning

  self.tism.setSystemState('EONET_categories', categories)
