#!/usr/bin/env python3

import openai
from random import choice

from phrases.default import beforeResearch

async def handleResponse(ctx, response):
  await ctx.send(response)

async def parsePrompt(self, ctx, prompt):
  await ctx.send(choice(beforeResearch))

  openai.api_key = self.token
  if 'The' in prompt:
    try:
      response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=50
      )
    except:
      return False
    else:
      return response

  if 'Is' in prompt:
    try:
      response = openai.Completion.create(
        engine="davinci-instruct-beta",
        prompt=prompt,
        max_tokens=100
      )
    except:
      return False
    else:
      return response