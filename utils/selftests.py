#!/usr/bin/env python3

import openai

from data.airesponse import OpenAIResponse
from logs import errors as ugh, warnings as warn
import phrases.system as syx
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

async def openAiSelftest(self, situation):
  openai.api_key  = self.subroutines['AI']
  engine          = 'ada'
  max_tokens      = 6
  prompt          = 'Q: Ping!\nA: Pong.\nQ: Ping!!\nA: ...Pong.\nQ: Ping--\nA: '
  stop_seq        = ['\n']

  try:
    response = openai.Completion.create(
      engine=engine,
      prompt=prompt,
      max_tokens=max_tokens,
      stop=stop_seq
    )
    res = OpenAIResponse(response)

  except Exception as e:
    self.tism.setSystemState('AI', 'DOWN')
    exceptionMessage = f'{syx.openai_selftest}: {e}'
    situation.errors.append(exceptionMessage)
    return False

  else:
    self.tism.setSystemState('AI', 'UP')
    situation.status.append(f'{syx.openai_selftest_response.format(engine)}: "{res.text[0]}"')
    return response
