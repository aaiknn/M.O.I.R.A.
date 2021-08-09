#!/usr/bin/env python3

import openai
from random import choice

from data.airesponse import OpenAIResponse
from phrases.default import beforeResearch, promptPlease, promptTimeout, onesidedBye
from utils.commands import checkForHighPermissions, requestPermission

async def handleResponse(self, ctx, response):
  _obj = OpenAIResponse(response)
  for choice in _obj.choices:
    fReason   = choice['finish_reason']
    text      = choice['text']

    message = f'{text}\n\n`Stopped because: {fReason}`'
    await self.send(ctx, message)

  await self.send(ctx, f'```txt\nID: {_obj.id}, Date: {_obj.date}, Object: {_obj.thing}, Model: {_obj.model}```')

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
    errorMessage = f'Creating OpenAI Completion: {e}'
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
      errorMessage = f'Waiting for authorised prompt: {e}'
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
