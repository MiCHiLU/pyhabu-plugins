from twisted.internet import reactor, threads
from twisted.internet.defer import Deferred

import feedparser


class Main(object):
    def __init__(self, config, environ):
        self.config = config

    def fetch(self):
        return feedparser.parse(open(self.config["path"]).read())

    def gotRSS(self, result, deferred):
        deferred.callback(result)
        return result

    def gotErr(self, failure, deferred):
        deferred.errback(failure)

    def execute(self, cotent):
        deferred = Deferred()
        threads.deferToThread(self.fetch).addCallback(
            self.gotRSS, deferred).addErrback(
            self.gotErr, deferred)
        return deferred


def create(config, environ):
    return Main(config, environ)

