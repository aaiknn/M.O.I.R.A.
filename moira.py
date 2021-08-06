#!/usr/bin/env python3

from asyncio import sleep
from os import environ as env
from random import choice
from sessions.session import MoiraSession
from discord import DMChannel, TextChannel
from dotenv import load_dotenv

from logs import errors as ugh, status, warnings as warn
from phrases.default import basicScriptFail, busyState as busyPhrase, ha, initialPrompt, misc, nevermindedThen
from phrases.default import subroutineUnreachable as currentlyNot, unsureAboutQualifiedTopic as unsure, zerosidedBye

from sessions.core import MOIRA
from sessions.royub import Event, RoyUB
from sessions.tism import MoiraInfamousStateMachine as MISM
from sessions.session import MoiraSession
from sessions.users import SessionAdmin, SessionUser

from settings import prefs

from utils.administration import mindThoseArgs
from utils.db import DBSetup
from utils.prompts import handleResponse, parsePrompt, waitForAuthorisedPrompt
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

moira = MOIRA(
  moira_prefix,
  moira_nickname,
  moira_administrator_role,
  moira_user_role,
  moira_patience,
  subroutines = {
    'AI': openai_api_token,
    'DB': ''
  },
  webhook = {
    'id': moira_hooks_logs_id,
    'token': moira_hooks_logs_token
  }
)

moira.db = DBSetup(
  mongodb_cluster_domain,
  mongodb_cluster_name,
  mongodb_cluster_username,
  mongodb_cluster_userpass,
  mongodb_db_general,
  mongodb_collection_general
)

moira.mQ = []
moira.tism = MISM(
  busyKey           = 'busy',
  promptHistoryKey  = 'promptHistory',
  sessionKey        = 'busyWith',
  systemsKey        = 'subroutines'
)

moira.tism.setState(
  moira.tism.systemsKey, {
    'AI': 'DOWN',
    'DB': 'DOWN'
})

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
  moira.tism.resetPromptHistory()
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

  if not openai_api_token:
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
    if str.lower(moira.nickname) in str.lower(message.content):
      await sleep(2)
      await message.add_reaction(prefs.mPref_reaction_meta)

  await moira.process_commands(message)

# COMMANDS
@moira.command(
  name=moira.nickname,
  pass_context=True
)
async def initialPrompting(ctx):
  m = ctx.message
  chad = ctx.author.id
  chid = ctx.channel.id
  sessionUser = None

  if moira.administrator:
    for entry in ctx.author.roles:
      if str(moira.administrator) in str(entry.name):
        sessionUser = SessionAdmin(chad)
        break

  if not sessionUser and moira.regularUser:
    for entry in ctx.author.roles:
      if str(moira.regularUser) in str(entry.name):
        sessionUser = SessionUser(chad)
        break

  if not sessionUser:
    return

  outcome = await mindThoseArgs(moira, ctx, sessionUser, m)
  if outcome == 'DONE':
    return

  angryState = ctx.author.id in moira.tism.state['angryAt'] and len(moira.tism.state['angryAt'][ctx.author.id]) > 0
  if angryState:
    return

  busyState = moira.tism.getBusyState(chid)
  if busyState != 'FALSE':
    await ctx.send(choice(busyPhrase))
    moira.tism.queue('promptQueue', chid, m)
    moira.mQ.append(m.id)
    return

  if type(ctx.channel) == DMChannel:
    await moira.send(ctx, misc['notInDMs'])

  elif type(ctx.channel) == TextChannel:
    session = MoiraSession(ctx, moira, sessionUser)
    await session.createSession(chid, phrase=choice(initialPrompt))
    message = await waitForQualificationInput(session.handler, session.ctx)
    if message:
      session.message = message.content
    else:
      await session.exitSession(chid)
      return

    try:
      await qualifyInput(moira, chid, message)

    except InterruptedError:
      await session.exitSession(chid, response=choice(nevermindedThen))
      return

    except ModuleNotFoundError:
      if sessionUser.role == 'admin':
        await session.exitSession(chid, response=choice(currentlyNot))
      else:
        await session.exitSession(chid, response=choice(unsure))
      return

    except NotImplementedError:
      await session.exitSession(chid, response=choice(unsure))
      return

    except TypeError:
      if sessionUser.role == 'regular':
        reason = prefs.mPref_wrongType
        duration = 4
        await moira.send(ctx, choice(zerosidedBye), 2)
        e = Event('stormoff')
        await e.run(ctx, reason, duration)
      else:
        await session.exitSession(chid, response=choice(ha))
      return

    except TimeoutError:
      print('Prompt timeout.')
      await session.exitSession(chid)
      return

    except Exception as e:
      print('Oh no no no. (This message is really hardly ever printed. Have fun troubleshooting!)')
      print(e)
      await session.exitSession(chid)
      return

    sessionState = session.getState(chid)
    subroutine = sessionState['active_subroutine']

    if subroutine == 'AI':
      response = ''
      prompt = await waitForAuthorisedPrompt(moira, ctx, sessionUser)
      if prompt:
        response = await parsePrompt(moira, ctx, prompt.content)
        if response:
          await handleResponse(moira, ctx, response)
        else:
          await moira.send(ctx, misc['failsafe'])
        moira.tism.addToPromptHistory(chid, chad, prompt, response)
      moira.tism.removeFromSessionState(chid, 'active_subroutine')

    moira.tism.setBusyState(chid, 'FALSE')
    moira.tism.setSessionState(chid, None)

    if m.id in moira.mQ:
      moira.tism.dequeue('promptQueue', chid, m)
      moira.mQ.remove(m.id)

  else:
    await moira.send(ctx, misc['notInOther'])

moira.run(str(env.get('DISCORD_API_TOKEN')))
