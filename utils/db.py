#!/usr/bin/env python3

from bson.objectid import ObjectId
from pymongo import MongoClient
from random import choice

import logs.errors as ugh
from phrases.default import connectionSuccessful
import phrases.system as syx

class DBSetup:
  def __init__(self, domain, name, username, userpass, database, collection):
    self.cluster_name = name
    self.db_name      = database
    self.coll_name    = collection
    self.uri          = f'mongodb+srv://{username}:{userpass}@{name}.{domain}{database}?retryWrites=true&w=majority'
    self.errors       = []
    self.state        = { 'meta': None }

    for item in [
      domain,
      username,
      userpass
    ]:
      if not item:
        self.errors.append(ugh.database_env_missing)

  async def selfTest(self):
    client = MongoClient(self.uri)
    try:
      db = client[self.db_name]
      db[self.coll_name]
    except Exception as e:
      self.errors.append(e)
      raise ConnectionAbortedError
    else:
      client.close
      return True

  async def retrieveMeta(self, handler):
    client = MongoClient(self.uri)
    try:
      db          = client[self.db_name]
      collection  = db[self.coll_name]
      meta        = collection.find_one({'meta': True})

      if meta:
        handler.db.state['meta'] = {
          '_id': str(meta['_id']),
          'HEAD': str(meta['HEAD']),
          'TAIL': str(meta['TAIL'])
        }

      else:
        documentId = collection.insert_one({'meta': True}).inserted_id
        handler.db.state['meta'] = {
          '_id': str(documentId),
          'HEAD': None,
          'TAIL': None
        }
    except Exception as e:
      self.errors.append(f'handler.db.state: {e}')
      raise e
    else:
      client.close
      return True

class DBConnection:
  def __init__(self, dbSetupObj):
    self.client = ''
    self.setup  = dbSetupObj
    self.state  = dbSetupObj.state
    self.errors = []

  async def connect(self):
    self.client = MongoClient(self.setup.uri)
    try:
      db = self.client[self.setup.db_name]
      collection = db[self.setup.coll_name]
    except Exception as e:
      self.errors.append(f'{syx.connecting_to.format(self.setup.coll_name)}: {e}')
      raise ConnectionAbortedError
    else:
      return collection

  async def disconnect(self):
    try:
      self.client.close
    except Exception as e:
      self.errors.append(f'{syx.closing_client_connection}: {e}')
      raise e

  async def restoreState(self, tismStateObj, identifier='last'):
    state       = tismStateObj
    collection  = await self.connect()

    try:
      meta = collection.find_one({'meta': True})
      document = collection.find_one({'_id': meta['TAIL']})
    except Exception as e:
      self.errors.append(f'{syx.retrieving_tail_document}: {e}')
      raise e
    finally:
      await self.disconnect()

    state['angryAt']        = document['angryAt']
    state['promptHistory']  = document['promptHistory']
    state['promptQueue']    = document['promptQueue']

  async def storeState(self, tismStateObj, identifier):
    meta        = self.state['meta']
    currentHead = meta['HEAD']
    currentTail = meta['TAIL']

    collection = await self.connect()

    state = tismStateObj
    state['identifier'] = str(identifier)
    state['tail']       = None

    if currentTail:
      state['head'] = ObjectId(currentTail)
    else:
      state['head'] = None

    try:
      documentId = collection.insert_one(state).inserted_id
    except Exception as e:
      self.errors.append(f'{syx.inserting_state_document}: {e}')
      raise e

    newTail = str(documentId)
    if currentHead:
      newHead = currentHead
    else:
      newHead = str(documentId)

    try:
      updatedTail = collection.update_one({
        '_id': ObjectId(currentTail)
      }, { '$set': {
        'tail': documentId
      }})
      if not updatedTail.matched_count == 1:
        raise FileNotFoundError
    except Exception as e:
      self.errors.append(f'{syx.updating_last_tail_document}: {e}')
      raise e

    try:
      updatedMeta = collection.update_one({
        'meta': True
      }, { '$set': {
        'HEAD': ObjectId(newHead),
        'TAIL': ObjectId(newTail)
      }})
      if not updatedMeta.matched_count == 1:
        raise Warning
    except Exception as e:
      self.errors.append(f'{syx.updating_meta_document}: {e}')
      raise e

    newMeta = {
      'HEAD': newHead,
      'TAIL': newTail
    }

    await self.disconnect()
    return newMeta

async def dbConnect(handler, ctx, **options):
  database      = options.get('database')
  collection    = options.get('collection')
  callback      = options.get('callback')
  callbackArgs  = options.get('callbackArgs')

  client = MongoClient(handler.db.uri)

  try:
    if database:
      db = client[database]
    else:
      db = client[handler.db.db_name]
    if collection:
      db[collection]
    else:
      db[handler.db.coll_name]

    if callback:
      callback(callbackArgs)
  except Exception as e:
    errorMessage = f'dbConnect(): {e}'
    print(errorMessage)
    handler.db.errors.append(errorMessage)
    return False
  else:
    await handler.send(ctx, choice(connectionSuccessful))
    client.close
    return True
