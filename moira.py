#!/usr/bin/env python3

from asyncio import sleep
from os import environ as env
from random import choice
from discord import DMChannel, Intents, TextChannel
from discord.ext import commands
from dotenv import load_dotenv

import logs.errors as ugh
import logs.status as status
import logs.warnings as warn
from phrases.default import basicScriptFail, busyState as busyPhrase, initialPrompt, misc, nevermindedThen, subroutineUnreachable as currentlyNot, unsureAboutQualifiedTopic as unsure, zerosidedBye

from sessions.royub import Event, RoyUB
from sessions.tism import TheInfamousStateMachine as TISM

from settings import prefs

from utils.commands import waitForAuthorisedPrompt
from utils.db import DBSetup
from utils.general import texting
from utils.prompts import handleResponse, parsePrompt
from utils.qualification import qualifyInput, waitForQualificationInput
from utils.startup import dbSelftest, logTests

load_dotenv()

# ENV
noColour = env.get('NO_COLOR')

moira_hooks_logs_id = str(env.get('MOIRA_WEBHOOKS_LOGS_ID'))
moira_hooks_logs_token = str(env.get('MOIRA_WEBHOOKS_LOGS_TOKEN'))
moira_hooks_open_logs_id = str(env.get('MOIRA_WEBHOOKS_OPEN_LOGS_ID'))
moira_hooks_open_logs_token = str(env.get('MOIRA_WEBHOOKS_OPEN_LOGS_TOKEN'))
moira_nickname = str(env.get('MOIRA_NICKNAME'))
moira_patience = int(env.get('MOIRA_MAX_PROMPT_LOOPS'))
moira_prefix = str(env.get('MOIRA_PREFIX'))

moira_administrator_role = str(env.get('MOIRA_ADMIN_ROLE'))
moira_user_role = str(env.get('MOIRA_USER_ROLE'))

mongodb_cluster_domain = env.get('MONGODB_CLUSTER_DOMAIN')
mongodb_cluster_name = env.get('MONGODB_CLUSTER_NAME')
mongodb_cluster_username = env.get('MONGODB_CLUSTER_USERNAME')
mongodb_cluster_userpass = env.get('MONGODB_CLUSTER_USERPASS')
mongodb_db_general = env.get('MONGODB_DB_GENERAL')
mongodb_collection_general = env.get('MONGODB_DB_GENERAL_COLLECTION')

openai_api_token = str(env.get('OPENAI_API_TOKEN'))

# GLOBALS
globalErrors = []
globalStatus = []
globalWarnings = []

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

moira.administrator = moira_administrator_role
moira.regularUser = moira_user_role

moira.nickname = moira_nickname
moira.patience = moira_patience
moira.mQ = []
moira.tism = TISM()
moira.tism.setState(
  'subroutines', {
    'AI': 'DOWN',
    'DB': 'DOWN'
})
moira.token = openai_api_token
moira.webhook = {
  'id': moira_hooks_logs_id,
  'token': moira_hooks_logs_token
}

roy = RoyUB(
  moira,
  'verbal',
  moira_hooks_open_logs_id,
  moira_hooks_open_logs_token
)

# EVENTS
moira.remove_command("help")

roy.manageEvent('stormoff', roy.emitMemberTimeout)
roy.manageEvent('memberTimeout', roy.memberTimeout)

@moira.event
async def on_ready():
  print(status.discord_moira_onready.format(moira))

  moira.tism.setState('angryAt', {prefs.mPref_larry_name: prefs.mPref_larry_reason})
  moira.tism.resetBusyState()
  moira.tism.resetSessionState()
  moira.tism.setState('promptQueue', {})

  await dbSelftest(moira, globalErrors)

  for meh in moira.db.errors:
    globalErrors.append(meh)

  if not moira.administrator and not moira.regularUser:
    globalWarnings.append(warn.moira_admin_and_user_not_set)
  elif not moira.administrator:
    globalStatus.append(status.moira_admin_not_set)
  elif not moira.regularUser:
    globalStatus.append(status.moira_user_not_set)

  if not moira.token:
    globalWarnings.append(warn.openai_token_not_set)

  await logTests(
    noColour,
    globalErrors,
    globalWarnings,
    globalStatus,
    moira.webhook
  )

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
      await sleep(2)
      await message.add_reaction(prefs.mPref_reaction_meta)

  await moira.process_commands(message)

# COMMANDS
@moira.command(
  name=moira.nickname,
  pass_context=True
)
async def initialPrompting(ctx):
  user = ctx.author
  m = ctx.message
  chid = ctx.channel.id

  angryState = user.id in moira.tism.state['angryAt'] and len(moira.tism.state['angryAt'][user.id]) > 0
  if angryState:
    return

  busyState = moira.tism.getBusyState(chid)
  if busyState != 'FALSE':
    await ctx.send(choice(busyPhrase))
    moira.tism.queue('promptQueue', chid, m)
    moira.mQ.append(m.id)
    return

  roleCheck = False
  userRole = None

  if moira.administrator:
    for entry in user.roles:
      if str(moira.administrator) in str(entry.name):
        roleCheck = True
        userRole = 'admin'
        break

  if moira.regularUser and not userRole:
    for entry in user.roles:
      if str(moira.regularUser) in str(entry.name):
        roleCheck = True
        userRole = 'regular'
        break

  if not roleCheck:
    return

  moira.tism.setBusyState(chid, user.id)
  moira.tism.setSessionState(chid, userRole, user.id)

  if type(ctx.channel) == DMChannel:
    await texting(ctx)
    await ctx.send(misc['notInDMs'])

  elif type(ctx.channel) == TextChannel:
    await texting(ctx)
    await ctx.send(choice(initialPrompt))
    topic = await waitForQualificationInput(moira, ctx, user)

    try:
      await qualifyInput(moira, chid, topic.content)

    except InterruptedError:
      await ctx.send(choice(nevermindedThen))
      moira.tism.setBusyState(chid, 'FALSE')
      moira.tism.setSessionState(chid, None)
      return

    except ModuleNotFoundError:
      await ctx.send(choice(currentlyNot))
      moira.tism.setBusyState(chid, 'FALSE')
      moira.tism.setSessionState(chid, None)
      return

    except NotImplementedError:
      await ctx.send(choice(unsure))
      moira.tism.setBusyState(chid, 'FALSE')
      moira.tism.setSessionState(chid, None)
      return

    except TypeError:
      reason = prefs.mPref_wrongType
      duration = 4
      await texting(ctx, 2)
      await ctx.send(choice(zerosidedBye))
      e = Event('stormoff')
      await e.run(ctx, reason, duration)
      return

    except TimeoutError:
      print('Prompt timeout.')
      moira.tism.setBusyState(chid, 'FALSE')
      moira.tism.setSessionState(chid, None)
      return

    except:
      print('Oh no no no. (This message is really hardly ever printed. Have fun troubleshooting!)')
      moira.tism.setBusyState(chid, 'FALSE')
      moira.tism.setSessionState(chid, None)
      return

    prompt = await waitForAuthorisedPrompt(moira, ctx, user)
    if prompt:
      response = await parsePrompt(moira, ctx, prompt.content)
      if response:
        await handleResponse(ctx, response)
      else:
        await texting(ctx)
        await ctx.send(misc['failsafe'])

    if m.id in moira.mQ:
      moira.tism.dequeue('promptQueue', chid, m)
      moira.mQ.remove(m.id)

    moira.tism.setBusyState(chid, False)
    moira.tism.setSessionState(chid, None)

  else:
    await texting(ctx)
    await ctx.send(misc['notInOther'])

moira.run(str(env.get('DISCORD_API_TOKEN')))
