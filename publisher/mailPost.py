# -*- coding: utf-8 -*-
__author__ = 'mattn.jp@gmail.com'
__version__ = '0.1'

import smtplib
import urllib
import urlparse
import re
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEImage import MIMEImage
from email.Header import Header
from email.Utils import formatdate
from HTMLParser import HTMLParser
import habu.log as log

class _EnclosureParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.base = ""
    self.files = []

  def set_base(self, url):
    if url.endswith("/"):
      self.base = url + "index.html"
    else:
      self.base = url

  def handle_starttag(self, tag, attrs):
    if tag.lower() == "img":
      for attr in attrs:
        if attr[0] == "src":
          self.files.append(urlparse.urljoin(self.base, attr[1]))
          break

class MailPublisher(object):
  def __init__(self, config, environ):
    self.mailto = config.get("mailto", "mail to")
    self.mailfrom = config.get("mailfrom", "mail from")
    self.mailroute = config.get("mailroute", "mail route")
    self.encoding = config.get("encoding", "utf-8")

  def execute(self, content):
    try:
      if self.mailroute.has_key("host"):
        s = smtplib.SMTP(self.mailroute["host"])
      else:
        s = smtplib.SMTP()
      for entry in content["entries"]:
        html = """<html>
<body>
""" + entry["description"] + """
</body>
</html>"""
        msg = MIMEMultipart()
        msg['Subject'] = Header(entry["title"], self.encoding)
        msg['From'] = self.mailfrom
        msg['To'] = self.mailto
        msg['Date'] = formatdate()
        msg['X-Mailer'] = "pyhabu::mailPost %s" % __version__
        related = MIMEMultipart('related')
        alt = MIMEMultipart('alternative')
        related.attach(alt)
        ep = _EnclosureParser()
        try:
          ep.set_base(entry["link"])
          ep.feed(html)
        except Exception, e:
          pass
        finally:
          ep.close()
        cnt = 1
        for filename in ep.files:
          fp = urllib.urlopen(filename)
          headers = fp.info()
          if headers.has_key("content-type"):
            mimetype = headers["content-type"].replace("image/", "")
            name = "img%d.%s" % (cnt, mimetype)
            img = MIMEImage(fp.read(), mimetype, name=name)
            img['Content-ID'] = '<%s>' % name
            related.attach(img)
            html = re.compile(r"(<img.*>)").sub(
              lambda x:x.group(1).replace(filename, name), html)
            cnt += 1
        content = MIMEText(html.encode(self.encoding, "replace"), 'html', self.encoding)
        alt.attach(content)
        msg.attach(related)

        s.sendmail(self.mailfrom, self.mailto, msg.as_string())
        log.info("mailPost : commit")
    except Exception, e:
      log.error()
    finally:
      s.close()

def create(config, environ):
  return MailPublisher(config, environ)
