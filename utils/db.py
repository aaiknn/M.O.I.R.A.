#!/usr/bin/env python3

from pymongo import MongoClient

import logs.errors as ugh

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
    except:
      raise ConnectionAbortedError
    else:
      client.close
      return True

async def dbConnect(handler, ctx):
  client = MongoClient(handler.db.uri)

  try:
    db = client[handler.db.db_name]
    db[handler.db.coll_name]
  except:
    return False
  else:
    await ctx.send('Connection successful.')
    client.close
    return True
