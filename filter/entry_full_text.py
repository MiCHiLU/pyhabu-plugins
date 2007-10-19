__version__ = 'Alpha'

import os
import re
import yaml
from yaml import loader
import habu.log as log
import httplib2


class CustomLoader(loader.Loader):
    def check_plain(self):
        ch = self.peek()
        return ch not in u'\0 \t\r\n\x85\u2028\u2029-?:,[]{}#&*!|>\'\"@`'  \
            or (self.peek(1) not in u'\0 \t\r\n\x85\u2028\u2029'
                and (ch == u'-' or (not self.flow_level and ch in u'?:')))


class Main(object):
    def __init__(self, config, environ):
        self.config = config
        self.environ = environ

    def execute(self, context):
        assets_dir = self.environ.get("assets")
        if not assets_dir:
            log.debug(u"EFT: Not found assets directory.")
            return context
        eft_dict = load_assets(assets_dir)
        re_urls = dict([(re_key, re.compile(re_key, re.DOTALL)) for re_key in eft_dict.keys()])
        h = httplib2.Http()
        for entry in context["entries"]:
            for re_key, re_url in re_urls.items():
                #esp, content = h.request(entry["link"])
                if re_url.match(entry["link"]):
                    #content = re.compile(eft_dict[re_key], re.DOTALL).match(content)[0]
                    pass
                #entry["summary"] = content
        return context


def create(*argv, **kwargv):
    return Main(*argv, **kwargv)

def load_assets(assets_dir):
    eft_dict = dict()
    for assets_file in os.listdir(assets_dir):
        if not assets_file.endswith(".yaml"):
            continue
        assets_path = "%s/%s" % (assets_dir, assets_file)
        if not os.path.isfile(assets_path):
            continue
        try:
            yaml_dict = yaml.load(open(assets_path).read(), CustomLoader)
        except yaml.scanner.ScannerError, e:
            log.debug(u"EFT: ScannerError in %s. %s\n%s"
                % (assets_file, yaml_dict, e))
            continue
        eft_dict[yaml_dict.get("handle", yaml_dict.get("handle_force"))] = yaml_dict
    return eft_dict

