#!/usr/bin/env python3

from time import sleep

async def texting(ctx, duration=1):
  async with ctx.channel.typing():
    sleep(duration)