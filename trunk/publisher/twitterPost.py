# -*- coding: utf-8 -*-
__author__ = 'mattn.jp@gmail.com'
__version__ = '0.1'

from twitter import Api
import habu.log as log

class TwitterPublisher(object):
  def __init__(self, config, environ):
    self.username = config.get("username", "twitter username")
    self.password = config.get("password", "twitter password")

  def execute(self, content):
    try:
      api = Api(self.username, self.password)
      for entry in content["entries"]:
        message = entry["title"] + ":"
        if len(entry["summary"]):
          message += entry["summary"]
        else:
          message += entry["description"]
        message += " " + entry["link"]
        if len(message) > 159:
          message = message[0: 159] + "..."
        api.PostUpdate(message)
    except Exception, e:
      log.error()
    else:
      log.info("twitterPost : commit")

def create(config, environ):
  return TwitterPublisher(config, environ)
