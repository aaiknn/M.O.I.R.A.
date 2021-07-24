#!/usr/bin/env python3

from os import environ as env
from random import choice
from discord import DMChannel, Intents, TextChannel
from discord.ext import commands
from dotenv import load_dotenv
from time import sleep

import logs.errors as ugh
import logs.status as status
import logs.warnings as warn
from phrases.default import basicScriptFail, initialPrompt, misc
from utils.commands import waitingForInput
from utils.general import texting
from utils.prompts import handleResponse, parsePrompt
from utils.startup import logStartup

load_dotenv()

moira_hooks_logs_id = str(env.get('MOIRA_WEBHOOKS_LOGS_ID'))
moira_hooks_logs_token = str(env.get('MOIRA_WEBHOOKS_LOGS_TOKEN'))
moira_nickname = str(env.get('MOIRA_NICKNAME'))
moira_patience = int(env.get('MOIRA_MAX_PROMPT_LOOPS'))
moira_permission_role = str(env.get('MOIRA_PERM_ROLE'))
moira_prefix = str(env.get('MOIRA_PREFIX'))

openai_api_token = str(env.get('OPENAI_API_TOKEN'))

intents = Intents.default()
intents.members = True

moira = commands.Bot(
  command_prefix=moira_prefix,
  case_insensitive=True,
  intents=intents
)

moira.nickname = moira_nickname
moira.patience = moira_patience
moira.permission_role = moira_permission_role
moira.token = openai_api_token

moira.remove_command("help")

@moira.event
async def on_ready():
  print(status.discord_moira_onready.format(moira))
  warnings = []

  if not moira_permission_role:
    warnings.append(f'Warning: {warn.moira_permissions_not_set}')
    print(f'\nWarning: {warn.moira_permissions_not_set}')

  if not openai_api_token:
    warnings.append(f'Warning: {warn.openai_token_not_set}')
    print(f'\nWarning: {warn.openai_token_not_set}')
  
  if moira_hooks_logs_id and moira_hooks_logs_token:
    webhookId = moira_hooks_logs_id
    webhookToken = moira_hooks_logs_token
    await logStartup(webhookId, webhookToken, warnings)

@moira.event
async def on_command_error(ctx, err):
  await ctx.send(f"{choice(basicScriptFail)} `{err}`.")

@moira.event
async def on_error():
  print(ugh.moira_discord_error_event)

@moira.event
async def on_message(message):
  if message.author == moira.user:
      return
  
  if not message.content.startswith(moira_prefix):
    if moira.nickname in message.content:
      sleep(2)
      await message.add_reaction('\U0001f440')

  await moira.process_commands(message)

@moira.command(name=moira.nickname, pass_context=True)
async def initialPrompting(ctx):
  user = ctx.author

  if type(ctx.channel) == DMChannel:
    await texting(ctx)
    await ctx.send(misc['notInDMs'])

  elif type(ctx.channel) == TextChannel:
    await texting(ctx)
    await ctx.send(choice(initialPrompt))
    prompt = await waitingForInput(moira, ctx, user)
    if prompt:
      response = await parsePrompt(moira, ctx, prompt.content)
      if response:
        await handleResponse(ctx, response)
      else:
        await texting(ctx)
        await ctx.send(misc['failsafe'])

  else:
    await texting(ctx)
    await ctx.send(misc['notInOther'])

moira.run(str(env.get('DISCORD_API_TOKEN')))
