#!/usr/bin/env python3

from asyncio import sleep

termColours = {
  'boldred': '\x1b[1;31m',
  'boldyellow': '\x1b[1;33m',
  'colourend': '\x1b[0m',
  'colorend': 'colourend'
}

def getTermColour(key, noColor = False):
  if noColor:
    return ''
  else:
    return termColours[key]

async def texting(ctx, duration=1):
  async with ctx.channel.typing():
    sleep(duration)
