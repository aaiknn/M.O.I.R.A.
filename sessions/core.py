#!/usr/bin/env python3

from discord import Intents
from discord.ext.commands import Bot
from random import choice

from phrases.default import emptyMessage
from utils.general import texting

intents = Intents.default()
intents.members = True

class MOIRA(Bot):
  def __init__(self, prefix, nickname, admin, regularUser, patience, **options):
    super().__init__(
      prefix,
      case_insensitive=True,
      intents=intents
    )

    self.nickname       = nickname
    self.administrator  = admin
    self.regularUser    = regularUser
    self.patience       = patience
    self.subroutines    = options.get('subroutines')
    self.webhook        = options.get('webhook')

  async def send(self, ctx, m, duration=1, **options):
    isCode      = options.get('code')
    isDM        = options.get('dm')
    codeFormat  = options.get('codeFormat')
    embed       = options.get('embed')

    if len(m) > 1800:
      mList = [m[i:i+1800] for i in range(0, len(m), 1800)]
      for entry in mList:
        if isCode:
          format = codeFormat if codeFormat else 'txt'
          entry = f'```{format}\n{entry}```'

        await sendMessage(ctx, duration, entry, isDM)

    elif isCode:
      m = f'```txt\n{m}```'
      await sendMessage(ctx, duration, m, isDM)

    else:
      await sendMessage(ctx, duration, m, isDM, embed)

async def sendMessage(ctx, duration, m, isDM, embed=''):
  if len(m) == 0 and not embed:
    m += choice(emptyMessage)

  if isDM:
    await ctx.author.send(m, embed=embed)
  else:
    await texting(ctx, duration)
    await ctx.send(m, embed=embed)
