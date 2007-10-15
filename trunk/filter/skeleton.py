import habu.log as log


class Main(object):
    def __init__(self, config, environ):
        self.config = config
        self.environ = environ

    def execute(self, context):
        log.debug(u"Using skeleton.")
        return context


def create(*argv, **kwargv):
    return Main(*argv, **kwargv)

