"""filter.docstring

"""
import unittest
from StringIO import StringIO

import habu.log as log


__version__ = "Alpha"
MODNAME = "filter.docstring"


class Main(object):
    def __init__(self, config, environ):
        self.config = config
        self.environ = environ
        self.ignore = config.get("ignore", False)
        template = config.get("template")
        if template:
            try:
                template = open(template).read()
            except IOError:
                log.debug("%s: IOError in template." % MODNAME)
        if not template:
            template = "NON-TEMPLATE"
        self.template = template

    def execute(self, context):
        context["entries"] = [self.render(entry) for entry in context["entries"]]
        return context

    def render(self, entry, template=None):
        """
        >>> template = "%(__version__)s/%(__doc__)s/%(__author__)s"
        >>> entry = dict(
        ...     summary = '''
        ... \"\"\"SUMMARY.\"\"\"
        ... __author__ = "AUTHOR"
        ... __version__ = "VERSION"
        ... ''',
        ... )
        >>> create(dict(), dict()).render(entry, template)
        {'summary': 'VERSION/SUMMARY./AUTHOR'}
        """
        template = template or self.template
        mod = dict()
        try:
            exec entry["summary"] in mod
        except:
            if self.ignore:
                log.debug("%s: except ignore in %s." %
                    (MODNAME, entry["title"]))
            else:
                raise
        else:
            entry["summary"] = template % mod
        return entry


def create(*argv, **kwargv):
    return Main(*argv, **kwargv)


class Test(unittest.TestCase):
    def test(self):
        pass


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    unittest.main()
