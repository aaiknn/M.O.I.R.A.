#!/usr/bin/env python3

from aiohttp import ClientSession
from os import environ as env
from random import choice
from discord import AsyncWebhookAdapter
from discord import Embed
from discord import Intents
from discord import Webhook
from discord.ext import commands
from dotenv import load_dotenv
from time import gmtime as timestamp
from time import sleep

from phrases.default import basicScriptFail, beforeResearch, initialPrompt
from utils.commands import waitingForInput

load_dotenv()

moira_hooks_logs_id = str(env.get('MOIRA_WEBHOOKS_LOGS_ID'))
moira_hooks_logs_token = str(env.get('MOIRA_WEBHOOKS_LOGS_TOKEN'))
moira_patience = int(env.get('MOIRA_MAX_PROMPT_LOOPS'))
moira_permission_role = str(env.get('MOIRA_PERM_ROLE'))
moira_prefix = str(env.get('MOIRA_PREFIX'))

intents = Intents.default()
intents.members = True

moira = commands.Bot(
  command_prefix=moira_prefix,
  case_insensitive=True,
  intents=intents
)

class DiscordHooks:
  def __init__(self, id, token, adapter):
    self.hook = Webhook.from_url(
      f'https://discordapp.com/api/webhooks/{id}/{token}',
      adapter=adapter
    )

moira.patience = moira_patience
moira.permission_role = moira_permission_role

moira.remove_command("help")


@moira.event
async def on_ready():
  print('Successfully logged in as {0.user}'.format(moira))
  
  s = ClientSession()
  async with s:
    t = timestamp()
    log = DiscordHooks(
      moira_hooks_logs_id,
      moira_hooks_logs_token,
      AsyncWebhookAdapter(s)
    )
    await log.hook.send(
      embed=Embed(
        title='Moira up!',
        description=f'It\'s true.\nUTC Timestamp: {t.tm_mday}-{t.tm_mon}-{t.tm_year} at {t.tm_hour}:{t.tm_min}:{t.tm_sec}.'
      )
    )
  await s.close()

@moira.event
async def on_command_error(ctx, err):
  await ctx.send(f"{choice(basicScriptFail)} `{err}`.")

@moira.event
async def on_message(message):
  if message.author == moira.user:
      return
  
  if not message.content.startswith(moira_prefix):
    if 'moira' in message.content:
      sleep(2)
      await message.add_reaction('\U0001f440')

  await moira.process_commands(message)

@moira.command(name="moira", pass_context=True)
async def askForInput(ctx):
  user = ctx.author
  await ctx.send(choice(initialPrompt))
  sleep(1)
  prompt = await waitingForInput(moira, ctx, user)
  if prompt:
    await ctx.send(prompt.content)
    await ctx.send(choice(beforeResearch))

moira.run(str(env.get('DISCORD_API_TOKEN')))