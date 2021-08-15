#!/usr/bin/env python3

from json import loads

class OpenAIResponse:
  def __init__(self, response):
    self.raw = response
    self.obj = loads(str(response), strict=False)

    self.choices  = self.obj['choices']
    self.date     = self.obj['created']
    self.id       = self.obj['id']
    self.model    = self.obj['model']
    self.thing    = self.obj['object']

    self.text     = []
    for choice in self.choices:
      self.text.append(choice['text'])
