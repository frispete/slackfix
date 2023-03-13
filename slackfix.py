#!/usr/bin/python3
"""
Usage: {appname} [-hVv]
       -h, --help           this message
       -V, --version        print version and exit
       -v, --verbose        verbose mode (cumulative)

Description:
Wrapper script, attempts to execute Slack with the correct URI argument.

The electron environment in Tumbleweed seems to suffer from a flaw similar to
kde-open5 [1], that results in Slack failing to open the workspace correctly.
It mangles the host part of the URI into lowerspace, which is Slack's undoing.

Background
Generic URL handling is defined in RFC 3986: URI Generic Syntax, where
section 3.2.2 says: "The host subcomponent is case-insensitive"). The electron
environment appears to conform with that in newer releases.

The simplest place to solve this would be also on the Slack side by accepting a
lower case host part of the internal slack:// URI, or it shouldn't use any host
part at all (slack:///...).

Since they are aware of this issue since several month, we cannot rely on a
fix provided anytime soon [3], so here's a (hopefully) suitable antidote.

External resources:
[1] KDE issue: https://bugs.kde.org/show_bug.cgi?id=429408
[2] https://www.rfc-editor.org/rfc/rfc3986
[3] With the usual outcome: we do not support openSUSE Tumbleweed, use the
    snap packages! Needless to say, they suffer from the same issue.

Prerequisites/Requirements:
Current Slack RPM installed (main executable: /usr/lib/slack/slack,
/usr/bin/slack is a symlink to it).

Copyright:
(c)2023 by {author}

License:
{license}
"""
# vim:set et ts=8 sw=4:

__version__ = '0.1'
__author__ = 'Hans-Peter Jansen <hpj@urpla.net>'
__license__ = 'GNU GPL v2 - see http://www.gnu.org/licenses/gpl2.txt for details'
__homepage__ = 'https://github.com/frispete/kde-open5-slackfix'


import os
import re
import sys
import time
import getopt
import locale
import select
import subprocess
from urllib.parse import urlparse

class gpar:
    """Global parameter class"""
    __slots__ = ()
    appdir, appname = os.path.split(sys.argv[0])
    if appdir == '.':
        appdir = os.getcwd()
    if appname.endswith('.py'):
        appname = appname[:-3]
    pid = os.getpid()
    version = __version__
    author = __author__
    license = __license__
    homepage = __homepage__
    slackbin = '/usr/bin/slack'
    slackobj = '/usr/lib/slack/slack'
    slackargs = ['--enable-crashpad']


stdout = lambda *msg: print(*msg, file = sys.stdout, flush = True)
stderr = lambda *msg: print(*msg, file = sys.stderr, flush = True)


class Log:
    """Minimal logging implementation (for performance reasons)"""
    __slots__ = ('_name', '_level', '_datefmt')

    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    _levelToName = {
        CRITICAL: 'CRITICAL',
        ERROR: 'ERROR',
        WARNING: 'WARNING',
        INFO: 'INFO',
        DEBUG: 'DEBUG',
        NOTSET: 'NOTSET',
    }

    def __init__(self, appname, level):
        self._name = appname
        self._level = level
        # internal
        self._datefmt = '%Y-%m-%d %H:%M:%S'

    def getLevel(self):
        return self._level

    def setLevel(self, level):
        oldlevel = 0
        if level and level in Log._levelToName:
            oldlevel = self._level
            self._level = level
        return oldlevel

    def log(self, level, msg):
        if level >= self._level:
            lvl = self._levelToName[level]
            ts = time.strftime(self._datefmt)
            stderr(f'{ts} {lvl}: [{self._name}] {msg}')

    def critical(self, msg):
        self.log(Log.CRITICAL, msg)

    def error(self, msg):
        self.log(Log.ERROR, msg)

    def warning(self, msg):
        self.log(Log.WARNING, msg)

    def info(self, msg):
        self.log(Log.INFO, msg)

    def debug(self, msg):
        self.log(Log.DEBUG, msg)

log = Log(gpar.appname, Log.WARNING)


def exit(ret = 0, msg = None, usage = False):
    """Terminate process with optional message and usage"""
    if msg:
        stderr(f'{gpar.appname}: {msg}')
    if usage:
        stderr(__doc__.format(**gpar.__dict__))
    sys.exit(ret)


def run():
    """run slack, and wait for a certain url pattern: fix it, and execute slack again with the fixed argument"""
    log.info(f'[{gpar.pid}]: started')
    args = [gpar.slackbin]
    objargs = []
    done = False

    with subprocess.Popen(args,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          text = True) as p:
        for line in p.stdout:
            if line.endswith('\n'):
                line = line[:-1]
            log.info(line)
            match = re.search('"url": "(slack://.*)"', line)
            if match and not done:
                url = match.group(1)
                log.info(f'slack url detected: {url}')
                poop = urlparse(url)
                poop = poop._replace(netloc = poop.netloc.upper())
                url = poop.geturl()
                log.info(f'new url: {url}')
                objargs = [gpar.slackobj, *gpar.slackargs, url]
                # spawn a new process
                pid = os.fork()
                if pid == 0:
                    log.info(f'execute: {objargs}')
                    try:
                        os.execvp(objargs[0], objargs)
                    except Exception as e:
                        log.error(e)
                else:
                    done = True

    log.info(f'finished')

    return 0


def main(argv = None):
    """Command line interface and console script entry point."""
    if argv is None:
        argv = sys.argv[1:]

    try:
        optlist, args = getopt.getopt(argv, 'hVv',
            ('help', 'version', 'verbose')
        )
    except getopt.error as msg:
        exit(1, msg, True)

    for opt, par in optlist:
        if opt in ('-h', '--help'):
            exit(usage = True)
        elif opt in ('-V', '--version'):
            exit(msg = 'version %s' % gpar.version)
        elif opt in ('-v', '--verbose'):
            log.setLevel(log.getLevel() - 10)

    if args:
        exit(1, 'does not take any arguments', True)

    try:
        return run()
    except KeyboardInterrupt:
        return 3    # SIGQUIT


if __name__ == '__main__':
    sys.exit(main())

