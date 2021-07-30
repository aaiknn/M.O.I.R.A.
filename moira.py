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
from phrases.default import basicScriptFail, busyState, initialPrompt, misc, zerosidedBye

from sessions.tism import TheInfamousStateMachine as TISM

from utils.commands import waitForAuthorisedPrompt
from utils.db import DBSetup
from utils.general import texting
from utils.prompts import handleResponse, parsePrompt
from utils.qualification import logStrongEmotionsToDiscord as stormoff, qualifyInput, waitForQualificationInput
from utils.startup import dbSelftest, logTests

load_dotenv()

noColour = env.get('NO_COLOR')

moira_hooks_logs_id = str(env.get('MOIRA_WEBHOOKS_LOGS_ID'))
moira_hooks_logs_token = str(env.get('MOIRA_WEBHOOKS_LOGS_TOKEN'))
moira_hooks_open_logs_id = str(env.get('MOIRA_WEBHOOKS_OPEN_LOGS_ID'))
moira_hooks_open_logs_token = str(env.get('MOIRA_WEBHOOKS_OPEN_LOGS_TOKEN'))
moira_nickname = str(env.get('MOIRA_NICKNAME'))
moira_patience = int(env.get('MOIRA_MAX_PROMPT_LOOPS'))
moira_permission_role = str(env.get('MOIRA_PERM_ROLE'))
moira_prefix = str(env.get('MOIRA_PREFIX'))

mongodb_cluster_domain = env.get('MONGODB_CLUSTER_DOMAIN')
mongodb_cluster_name = env.get('MONGODB_CLUSTER_NAME')
mongodb_cluster_username = env.get('MONGODB_CLUSTER_USERNAME')
mongodb_cluster_userpass = env.get('MONGODB_CLUSTER_USERPASS')
mongodb_db_general = env.get('MONGODB_DB_GENERAL')
mongodb_collection_general = env.get('MONGODB_DB_GENERAL_COLLECTION')

openai_api_token = str(env.get('OPENAI_API_TOKEN'))

intents = Intents.default()
intents.members = True

moira = commands.Bot(
  command_prefix=moira_prefix,
  case_insensitive=True,
  intents=intents
)

moira.db = DBSetup(
  mongodb_cluster_domain,
  mongodb_cluster_name,
  mongodb_cluster_username,
  mongodb_cluster_userpass,
  mongodb_db_general,
  mongodb_collection_general
)

moira.nickname = moira_nickname
moira.patience = moira_patience
moira.permission_role = moira_permission_role
moira.mQ = []
moira.tism = TISM()
moira.token = openai_api_token

moira.remove_command("help")

moira.tism.setState(
  'subroutines', {
    'AI': 'DOWN',
    'DB': 'DOWN'
})

globalErrors = []
globalWarnings = []

@moira.event
async def on_ready():
  print(status.discord_moira_onready.format(moira))

  moira.tism.setState('angryAt', {'Larry': 'I just don\'t like Larry.'})
  moira.tism.setState('busy', False)
  moira.tism.setState('busyWith', '')
  moira.tism.setState('promptQueue', {})

  await dbSelftest(moira, globalErrors)

  for meh in moira.db.errors:
    globalErrors.append(meh)

  if not moira_permission_role:
    globalWarnings.append(warn.moira_permissions_not_set)

  if not openai_api_token:
    globalWarnings.append(warn.openai_token_not_set)

  await logTests(noColour, globalErrors, globalWarnings, moira_hooks_logs_id, moira_hooks_logs_token)

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
  m = ctx.message
  chn = ctx.channel.name

  if user.id in moira.tism.state['angryAt'] and len(moira.tism.state['angryAt'][user.id]) > 0:
    return

  if moira.tism.state['busy'] == False:
    moira.tism.setState('busy', True)

    if type(ctx.channel) == DMChannel:
      await texting(ctx)
      await ctx.send(misc['notInDMs'])

    elif type(ctx.channel) == TextChannel:
      await texting(ctx)
      await ctx.send(choice(initialPrompt))

      topic = await waitForQualificationInput(moira, ctx, user)

      try:
        await qualifyInput(moira, topic.content)
      except InterruptedError:
        moira.tism.setState('busy', False)
        return
      except ModuleNotFoundError:
        print('Oh no')
      except NotImplementedError:
        print('Oh no no')
      except TypeError:
        # TODO: rework this.
        await texting(ctx, 2)
        await ctx.send(choice(zerosidedBye))

        reason = 'Not my type.'
        moira.tism.queue('angryAt', user.id, reason)

        if moira_hooks_open_logs_id and moira_hooks_open_logs_token:
          webhookId = moira_hooks_open_logs_id
          webhookToken = moira_hooks_open_logs_token
          await stormoff(webhookId, webhookToken, moira.nickname, user.name, 1)

        sleep(60 * 1)

        moira.tism.dequeue('angryAt', user.id, reason)
      except:
        print('Oh no no no')
      else:
        matter = moira.tism.getState('busyWith')
        await ctx.send(matter)

      prompt = await waitForAuthorisedPrompt(moira, ctx, user)
      if prompt:
        response = await parsePrompt(moira, ctx, prompt.content)
        if response:
          await handleResponse(ctx, response)
        else:
          await texting(ctx)
          await ctx.send(misc['failsafe'])

      if m.id in moira.mQ:
        moira.tism.dequeue('promptQueue', chn, m)
        moira.mQ.remove(m.id)

      moira.tism.setState('busy', False)

    else:
      await texting(ctx)
      await ctx.send(misc['notInOther'])

  else:
    await ctx.send(choice(busyState))
    moira.tism.queue('promptQueue', chn, m)
    moira.mQ.append(m.id)

moira.run(str(env.get('DISCORD_API_TOKEN')))
