#!/usr/bin/env python3

from pymongo import MongoClient

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
        self.errors.append(f'Uh-oh: A crucial env variable hasn\'t been set.')

  async def selfTest(self):
    client = MongoClient(self.uri)
    try:
      db = client[self.db_name]
      db[self.coll_name]
    except:
      return False
    else:
      client.close
      return True

async def dbConnect(self):
  client = MongoClient(self.db.uri)