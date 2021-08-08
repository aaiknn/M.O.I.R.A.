#!/usr/bin/env python3

import logs.errors as ugh

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
