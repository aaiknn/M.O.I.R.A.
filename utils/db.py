#!/usr/bin/env python3

from bson.objectid import ObjectId
from pymongo import MongoClient
from random import choice

import logs.errors as ugh
from phrases.default import connectionSuccessful

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
      db = client[self.db_name]
      collection = db[self.coll_name]
      meta = collection.find_one({'meta': True})
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
    self.setup  = dbSetupObj
    self.state  = dbSetupObj.state
    self.errors = []

  async def storeState(self, stateObj, identifier):
    meta        = self.state['meta']
    currentHead = meta['HEAD']
    currentTail = meta['TAIL']

    client = MongoClient(self.setup.uri)

    try:
      db = client[self.setup.db_name]
      collection = db[self.setup.coll_name]
    except Exception as e:
      self.errors.append(f'Connecting to self.setup.coll_name: {e}')
      raise ConnectionAbortedError

    state = stateObj
    state['identifier'] = str(identifier)
    state['tail']       = None

    if currentTail:
      state['head'] = ObjectId(currentTail)
    else:
      state['head'] = None

    try:
      documentId = collection.insert_one(state).inserted_id
    except Exception as e:
      self.errors.append(f'Inserting state document: {e}')
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
      self.errors.append(f'Updating current tail document: {e}')
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
      self.errors.append(f'Updating meta document: {e}')
      raise e

    newMeta = {
      'HEAD': newHead,
      'TAIL': newTail
    }

    try:
      client.close
    except Exception as e:
      self.errors.append(f'Closing client session: {e}')
      raise e

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
    print(e)
    handler.db.errors.append(e)
    return False
  else:
    await handler.send(ctx, choice(connectionSuccessful))
    client.close
    return True
