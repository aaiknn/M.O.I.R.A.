#!/usr/bin/env python3

from os import environ
from random import choice
from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv
from time import sleep

from phrases.default import basicScriptFail, beforeResearch, initialPrompt
from utils.commands import waitingForInput

load_dotenv()

moira_patience = int(environ.get('MOIRA_MAX_PROMPT_LOOPS'))
moira_permission_role = str(environ.get('MOIRA_PERM_ROLE'))
moira_prefix = str(environ.get('MOIRA_PREFIX'))

intents = Intents.default()
intents.members = True

moira = commands.Bot(
  command_prefix=moira_prefix,
  case_insensitive=True,
  intents=intents
)

moira.patience = moira_patience
moira.permission_role = moira_permission_role

moira.remove_command("help")

@moira.event
async def on_ready():
  print('Successfully logged in as {0.user}'.format(moira))

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

moira.run(str(environ.get('DISCORD_API_TOKEN')))