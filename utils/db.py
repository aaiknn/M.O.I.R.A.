#!/usr/bin/env python3

from pymongo import MongoClient
from random import choice

import logs.errors as ugh
from phrases.default import connectionSuccessful

class DBSetup:
  def __init__(self, domain, name, username, userpass, database, collection):
    self.cluster_name = name
    self.db_name = database
    self.coll_name = collection
    self.uri = f'mongodb+srv://{username}:{userpass}@{name}.{domain}{database}?retryWrites=true&w=majority'
    self.errors = []

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
      self.db.errors.append(e)
      raise ConnectionAbortedError
    else:
      client.close
      return True

class DBConnection:
  def __init__(self, dbSetupObj):
    self.db = dbSetupObj
    self.db.errors = []

  async def storeState(self, stateObj, identifier):
    client = MongoClient(self.db.uri)
    try:
      db = client[self.db.db_name]
      collection = db[self.db.coll_name]
    except Exception as e:
      self.db.errors.append(e)
      raise ConnectionAbortedError
    else:
      state = stateObj
      state['identifier'] = str(identifier)
      try:
        documentId = collection.insert_one(state).inserted_id
      except Exception as e:
        self.db.errors.append(e)
        raise e
      else:
        client.close
        return documentId
      finally:
        client.close

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
