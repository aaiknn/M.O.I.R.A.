#!/usr/bin/env python3

from asyncio import sleep
from os import environ as env
from random import choice
from discord import DMChannel, TextChannel
from dotenv import load_dotenv
from sys import path

from logs import status, warnings as warn
from phrases.default import basicScriptFail, busyState as busyPhrase, complete, ha, initialPrompt, misc, nevermindedThen
from phrases.default import subroutineUnreachable as currentlyNot, unsureAboutQualifiedTopic as unsure, zerosidedBye
import phrases.system as syx

from sessions.core import MOIRA
from sessions.exceptions import MoiraTypeError
from sessions.royub import Event, RoyUB
from sessions.session import MoiraSession
from sessions.situation import SessionSituation, Situation
from sessions.tism import MoiraInfamousStateMachine as MISM
from sessions.users import SessionAdmin, SessionUser

from settings import prefs

from utils.administration import mindThoseArgs
from utils.db import DBSetup
from utils.eonet import handleEonet
from utils.prompts import handleResponse, parsePrompt, waitForAuthorisedPrompt
from utils.qualification import qualifyInput, waitForQualificationInput
from utils.selftests import dbSelftest, eonetSelftest, openAiSelftest
from utils.startup import logTests
from utils.wsys import handleWsys

load_dotenv()

noColour = env.get('NO_COLOR')

moira_hooks_logs_id         = str(env.get('MOIRA_WEBHOOKS_LOGS_ID'))
moira_hooks_logs_token      = str(env.get('MOIRA_WEBHOOKS_LOGS_TOKEN'))
moira_hooks_open_logs_id    = str(env.get('MOIRA_WEBHOOKS_OPEN_LOGS_ID'))
moira_hooks_open_logs_token = str(env.get('MOIRA_WEBHOOKS_OPEN_LOGS_TOKEN'))

moira_nickname  = str(env.get('MOIRA_NICKNAME'))
moira_patience  = int(env.get('MOIRA_MAX_PROMPT_LOOPS'))
moira_prefix    = str(env.get('MOIRA_PREFIX'))

moira_administrator_role  = str(env.get('MOIRA_ADMIN_ROLE'))
moira_user_role           = str(env.get('MOIRA_USER_ROLE'))

mongodb_cluster_domain      = env.get('MONGODB_CLUSTER_DOMAIN')
mongodb_cluster_name        = env.get('MONGODB_CLUSTER_NAME')
mongodb_cluster_username    = env.get('MONGODB_CLUSTER_USERNAME')
mongodb_cluster_userpass    = env.get('MONGODB_CLUSTER_USERPASS')

mongodb_db_general          = env.get('MONGODB_DB_GENERAL')
mongodb_collection_general  = env.get('MONGODB_DB_GENERAL_COLLECTION')

openai_api_token  = str(env.get('OPENAI_API_TOKEN'))
nasa_api_token    = str(env.get('NASA_API_KEY'))

thisPath = path[0]
paths = {
  'reports': f'{thisPath}/reports/'
}

globals = Situation(
  noColour=noColour,
  errors=[],
  exceptions=[],
  status=[],
  warnings=[]
)

moira = MOIRA(
  moira_prefix,
  moira_nickname,
  moira_administrator_role,
  moira_user_role,
  moira_patience,
  subroutines = {
    'AI': openai_api_token,
    'DB': '',
    'EONET': nasa_api_token,
    'WSYS': []
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
    'DB': 'DOWN',
    'EONET': 'DOWN',
    'WSYS': 'SILENT'
})

roy = RoyUB(
  moira,
  'verbal',
  moira_hooks_open_logs_id,
  moira_hooks_open_logs_token
)

moira.remove_command('help')

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

  try:
    await dbSelftest(moira, globals)
    await eonetSelftest(moira, globals)
    await openAiSelftest(moira, globals)
  except:
    await globals.log(webhook=moira.webhook)
    globals.resetAll()

  for meh in moira.db.errors:
    globals.errors.append(meh)

  if not moira.administrator and not moira.regularUser:
    globals.warnings.append(warn.moira_admin_and_user_not_set)
  elif not moira.administrator:
    globals.status.append(status.moira_admin_not_set)
  elif not moira.regularUser:
    globals.status.append(status.moira_user_not_set)

  if not openai_api_token:
    globals.warnings.append(warn.openai_token_not_set)

  await logTests(
    moira.webhook,
    globals
  )
  globals.resetAll()

  if moira.tism.getSystemState('DB') == 'UP':
    await moira.db.retrieveMeta(moira)

@moira.event
async def on_command_error(ctx, err):
  errorMessage = syx.error_on_command.format(err)
  globals.errors.append(errorMessage)
  await globals.log(webhook=moira.webhook)
  globals.resetAll()
  await moira.send(ctx, f"{choice(basicScriptFail)} `{err}`.")

@moira.event
async def on_error(eventName):
  errorMessage = syx.error_on_event.format(eventName)
  globals.errors.append(errorMessage)
  await globals.log(webhook=moira.webhook)
  globals.resetAll()

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
  m                 = ctx.message
  chad              = ctx.author.id
  chid              = ctx.channel.id
  sessionUser       = None

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

  sit = SessionSituation(
    handler=moira,
    channelId=chid,
    noColour=noColour,
    sessionUser=sessionUser,
    userMessage=m,
    errors=[],
    exceptions=[],
    status=[],
    warnings=[]
  )

  try:
    if isinstance(sessionUser, SessionAdmin):
      outcome = await mindThoseArgs(moira, ctx, sit)
  except Exception as e:
    sit.exceptions.append(e)
    await sit.logIfNecessary(
      title='',
      webhook=moira.webhook
    )
    sit.resetAll()
  else:
    if outcome == 'DONE':
      return

  angryState = ctx.author.id in moira.tism.state['angryAt'] and len(moira.tism.state['angryAt'][ctx.author.id]) > 0
  if angryState:
    return

  busyState = moira.tism.getBusyState(chid)
  if busyState != 'FALSE':
    await moira.send(ctx, choice(busyPhrase))
    moira.tism.queue('promptQueue', chid, m)
    moira.mQ.append(m.id)
    return

  if type(ctx.channel) == DMChannel:
    await moira.send(ctx, misc['notInDMs'])

  elif type(ctx.channel) == TextChannel:
    session = MoiraSession(ctx, moira, sessionUser)
    await session.createSession(phrase=choice(initialPrompt))

    session.userMessage = await waitForQualificationInput(session.handler, session.ctx)
    if not session.userMessage:
      await session.exitSession()
      return

    try:
      await qualifyInput(moira, chid, session.userMessage)

    except InterruptedError:
      await session.exitSession(response=choice(nevermindedThen))
      return

    except ModuleNotFoundError:
      if sessionUser.role == 'admin':
        await session.exitSession(response=choice(currentlyNot))
      else:
        await session.exitSession(response=choice(unsure))
      return

    except NotImplementedError:
      await session.exitSession(response=choice(unsure))
      return

    except MoiraTypeError:
      if sessionUser.role == 'regular':
        reason = prefs.mPref_wrongType
        duration = 4
        await moira.send(ctx, choice(zerosidedBye), 2)
        e = Event('stormoff')
        await e.run(ctx, reason, duration)
      else:
        await session.exitSession(response=choice(ha))
      return

    except TimeoutError:
      await session.exitSession()
      return

    except Exception as e:
      errorMessage = syx.exception_qualifying_input.format(syx.exception, e)
      globals.exceptions.append(errorMessage)
      await globals.log(webhook=moira.webhook)
      await session.exitSession()
      return

    sessionState = session.getState()
    subroutine = sessionState['active_subroutine']

    if subroutine == 'AI':
      response  = ''
      prompt    = await waitForAuthorisedPrompt(moira, ctx, sessionUser)

      if prompt:
        response  = await parsePrompt(moira, ctx, prompt.content)

        if response:
          await handleResponse(moira, ctx, response)
        else:
          await moira.send(ctx, misc['failsafe'])
        moira.tism.addToPromptHistory(chid, chad, prompt, response)
      moira.tism.removeFromSessionState(chid, 'active_subroutine')
      await session.exitSession()

    elif subroutine == 'EONET':
      await handleEonet(ctx, session, sit)
      moira.tism.removeFromSessionState(chid, 'active_subroutine')
      await session.exitSession()

    elif subroutine == 'WSYS':
      await handleWsys(ctx, session, sit, paths)
      moira.tism.removeFromSessionState(chid, 'active_subroutine')
      await session.exitSession()

    if m.id in moira.mQ:
      moira.tism.dequeue('promptQueue', chid, m)
      moira.mQ.remove(m.id)

    await sit.logIfNecessary(title=syx.session_log, webhook=moira.webhook)
    sit.resetAll()

  else:
    await moira.send(ctx, misc['notInOther'])

moira.run(str(env.get('DISCORD_API_TOKEN')))
