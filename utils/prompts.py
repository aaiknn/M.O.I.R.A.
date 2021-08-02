#!/usr/bin/env python3

import openai
from random import choice

from data.airesponse import OpenAIResponse
from phrases.default import beforeResearch

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
    print(e)
    return False
  else:
    return response
