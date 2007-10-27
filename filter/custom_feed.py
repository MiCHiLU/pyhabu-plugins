__version__ = 'Alpha'

import re
import sets
from StringIO import StringIO

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from lxml import etree

import habu.log as log
from habu.habuutils import toUTF8
from habu.webutils import getPage


class CustomFeed(object):
    def __init__(self, config, environ):
        self.config = config
        self.proxy_host = environ.get("proxy_host", None)
        self.proxy_port = environ.get("proxy_port", 0)
        self.maxThread = config.setdefault("max-thread", 0)

    def execute(self, context):
        feed = [toUTF8(entry.get("link")) for entry in context["entries"]]
        self.feed = sets.Set(feed)
        try:
            self.feed.remove("")
        except KeyError:
            pass

        self.deferredList = [Deferred() for f in self.feed]

        maxThread = min(
            self.maxThread > 0 and self.maxThread or len(self.feed),
            len(self.feed))

        result = list()
        for i in range(0, maxThread):
            url = self.feed.pop()
            result.append(
                getPage(url, self.proxy_host, self.proxy_port).addCallback(
                    self.gotPage, url).addErrback(
                    self.gotErr)
            )
        return result

    def gotErr(self, failure):
        log.debug("filter.config gotErr")
        deferred = self.deferredList.pop()
        deferred.errback(failure)

    def gotPage(self, content, url):
        body = None
        capture = self.config.get("capture", None)
        if capture:
            matched = re.findall(capture, content, re.DOTALL|re.IGNORECASE)
            if matched:
                body = matched[0]
        if not body:
            body = content
        parser = etree.HTMLParser()

        try:
            charset = etree.parse(StringIO(content), parser).xpath('/html/head/meta[@http-equiv="Content-Type"]')[0].attrib.get("content")
        except IndexError:
            charset = None
        if charset:
            charset = charset.split("charset=")[-1].lower()
        title = etree.parse(StringIO(content), parser).xpath('/html/head/title')[0].text

        items = list()
        items.append(dict(
            summary_detail = dict(
                base = "",
                type = "text/html",
                value = unicode(body, charset or "utf-8", "ignore"),
                language = "",
            ),
            title = title,
            link = url,
        ))
        self.deferredList.pop()
        return dict(entries=items)


def create(config, environ):
    return CustomFeed(config, environ)

