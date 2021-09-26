#!/usr/bin/env python3

import openai
from random import choice

from data.airesponse import OpenAIResponse
from intentions.commands import confirm, reject
from phrases import system as syx, terms
from phrases.default import beforeResearch, decisionReceived, promptPlease, promptTimeout, onesidedBye
from phrases.default import permissionDenied, permissionGranted, requestPermission as reqPerm, requestTimeout
from sessions.users import SessionAdmin, SessionUser

def checkForHighPermissions(self, userObj):
  check = False

  if isinstance(userObj, SessionAdmin):
    return True
  elif isinstance(userObj, SessionUser):
    return False
  else:
    for role in userObj.roles:
      if self.administrator in str(role):
        check = True
        break

  return check

async def requestPermission(self, ctx):
  await self.send(ctx, choice(reqPerm))

  def check(m):
    decision  = str.lower(m.content)
    check     = checkForHighPermissions(self, m.author)

    if check and any(word in decision for word in confirm):
      return True
    elif any(word in decision for word in reject):
      raise PermissionError
    else:
      return False

  try:
    perm = await self.wait_for('message', check=check, timeout=60.0)
  except TimeoutError:
    await self.send(ctx, choice(requestTimeout))
    return False
  except PermissionError:
    await self.send(ctx, f'{choice(decisionReceived)} {choice(permissionDenied)}')
    return False
  except Exception as e:
    raise e
  else:
    await self.send(ctx, f'{choice(decisionReceived)} {choice(permissionGranted)}')
    return perm

async def handleResponse(self, ctx, response):
  _obj = OpenAIResponse(response)
  for choice in _obj.choices:
    fReason   = choice['finish_reason']
    text      = choice['text']

    message = f'{text}\n\n`{terms.openai_response_stopped_because}: {fReason}`'
    await self.send(ctx, message)

  meta  = f'```txt\n'
  meta += f'{terms.openai_response_prop_id}: {_obj.id}, '
  meta += f'{terms.openai_response_prop_date}: {_obj.date}, '
  meta += f'{terms.openai_response_prop_object}: {_obj.thing}, '
  meta += f'{terms.openai_response_prop_model}: {_obj.model}```'

  await self.send(ctx, meta)

async def parsePrompt(self, ctx, prompt):
  await self.send(ctx, choice(beforeResearch))

  openai.api_key  = self.subroutines['AI']
  max_tokens      = 50
  engine          = 'davinci'

  if 'detailed' in prompt:
    engine='davinci-instruct-beta'
    max_tokens=450

  try:
    async with ctx.channel.typing():
      response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        max_tokens=max_tokens
      )
  except Exception as e:
    errorMessage = f'{syx.creating_openai_completion}: {e}'
    print(errorMessage)
    return False
  else:
    return response

async def waitForAuthorisedPrompt(self, ctx, sessionUser):
  await self.send(ctx, choice(promptPlease))
  def check(m):
    return m.author == ctx.author

  for i in range(0, self.patience):
    try:
      prompt = await self.wait_for('message', check=check, timeout=60.0)
    except TimeoutError:
      if i == (self.patience - 1):
        await self.send(ctx, choice(onesidedBye), 2)
        break
      else:
        await self.send(ctx, choice(promptTimeout))
        continue
    except Exception as e:
      errorMessage = f'{syx.waiting_for_authorised_prompt}: {e}'
      print(errorMessage)
      raise e
    else:
      perm = checkForHighPermissions(self, sessionUser)
      if perm:
        return prompt
      else:
        req = await requestPermission(self, ctx)
        if req:
          return prompt

      break
