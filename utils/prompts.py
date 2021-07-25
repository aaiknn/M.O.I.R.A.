#!/usr/bin/env python3

import openai
# from json import load
from random import choice

from phrases.default import beforeResearch

async def handleResponse(ctx, response):
  await ctx.send(response)

async def parsePrompt(self, ctx, prompt):
  await ctx.send(choice(beforeResearch))

  openai.api_key = self.token

  ## defaults
  max_tokens=50

  if 'information' or 'info' in prompt:
    engine='davinci'
  if 'detailed' in prompt:
    engine='davinci-instruct-beta'
    max_tokens=450

  if engine:
    try:
      async with ctx.channel.typing():
        response = openai.Completion.create(
          engine=engine,
          prompt=prompt,
          max_tokens=max_tokens
        )
    except:
      return False
    else:
      return response
