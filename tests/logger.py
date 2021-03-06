#!/usr/bin/env python

"""
A simple logger.

Simple usage:
    import logger
    log = logger.Log('my_log.log', logger.Log.DEBUG)
    log('A line in the log at the default level (DEBUG)')
    log('A log line at WARN level', Log.WARN)
    log.info('log line issued at INFO level')

Based on the 'borg' recipe from [http://code.activestate.com/recipes/66531/].

Log levels styled on the Python 'logging' module.

Log output includes the module and line # of the log() call.
"""

import os
import sys
import datetime
import traceback


################################################################################
# A simple (?) logger.
################################################################################

class Log(object):

    __shared_state = {}                # this __dict__ shared by ALL instances

    # the predefined logging levels
    CRITICAL = 50
    ERROR = 40
    WARN = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    _level_num_to_name = {NOTSET: 'NOTSET',
                          DEBUG: 'DEBUG',
                          INFO: 'INFO',
                          WARN: 'WARN',
                          ERROR: 'ERROR',
                          CRITICAL: 'CRITICAL',
                         }

    # default maximum length of filename (enforced)
    DefaultMaxFname = 15


    def __init__(self, logfile=None, level=NOTSET, append=False,
                 max_fname=DefaultMaxFname):
        """Initialise the logging object.

        logfile  the path to the log file
        level    logging level - don't log below this level
        append   True if log file is appended to
        """

        # make sure we have same state as all other log objects
        self.__dict__ = Log.__shared_state

        # set some initial state
        self.max_fname = max_fname
        self.sym_level = 'NOTSET'      # set in call to check_level()
        self.level = self.check_level(level)

        # if not given logfile nme, make one up
        if logfile is None:
            logfile = '%s.log' % __name__

        # get correct options for rewrite or append of logfile
        log_options = 'w'
        if append:
            log_options = 'a'

        # test if we can use the file
        try:
            self.logfd = open(logfile, log_options)
            self.logfd.close()
        except IOError:
            # assume we have readonly filesystem
            basefile = os.path.basename(logfile)
            if sys.platform == 'win32':
                logfile = os.path.join('C:\\', basefile)
            else:
                logfile = os.path.join('~', basefile)

        # try to open logfile again
        self.logfd = open(logfile, log_options)

        self.logfile = logfile

        # announce time+date of opening logging and logging level
        self.debug('='*55)
        self.debug('Log started on %s, log level=%s'
                   % (datetime.datetime.now().ctime(),
                      self._level_num_to_name[level]))
        self.debug('-'*55)

    def check_level(self, level):
        """Check the level value for legality.

        level  a numeric logging level

        If 'level' is invalid, raise Exception.  If valid, return value.
        """

        try:
            level = int(level)
        except ValueError:
            msg = "Logging level invalid: '%s'" % str(level)
            print(msg)
            raise Exception(msg)

        if not 0 <= level <= 50:
            msg = "Logging level invalid: '%s'" % str(level)
            print(msg)
            raise Exception(msg)

        return level

    def set_level(self, level):
        """Set logging level."""

        level = self.check_level(level)

        # convert numeric level to symbolic
        sym = self._level_num_to_name.get(level, None)
        if sym is None:
            # not recognized symbolic but it's legal, so interpret as 'XXXX+2'
            sym_10 = 10 * (level/10)
            sym_rem = level - sym_10
            sym = '%s+%d' % (self._level_num_to_name[sym_10], sym_rem)

        self.level = level
        self.sym_level = sym

        self.critical('Logging level set to %02d (%s)' % (level, sym))

    def __call__(self, msg=None, level=None):
        """Call on the logging object.

        msg    message string to log
        level  level to log 'msg' at (if not given, assume self.level)
        """

        # get level to log at
        if level is None:
            level = self.level

        # are we going to log?
        if level < self.level or self.level < 0:
            return

        if msg is None:
            msg = ''

        # get time
        to = datetime.datetime.now()
        hr = to.hour
        min = to.minute
        sec = to.second
        msec = to.microsecond

        # caller information - look back for first module != <this module name>
        try:
            (_, mod_name) = __name__.rsplit('.', 1)
        except ValueError:
            mod_name = __name__

        frames = traceback.extract_stack()
        frames.reverse()

        for (fpath, lnum, mname, _) in frames:
            (fname, _) = os.path.basename(fpath).rsplit('.', 1)
            if fname != mod_name and fname != 'traceback':
                break

        # get string for log level
        loglevel = self._level_num_to_name[level]

        fname = fname[:self.max_fname]
        self.logfd.write('%02d:%02d:%02d.%06d|%8s|%*s:%-4d|%s\n'
                         % (hr, min, sec, msec, loglevel, self.max_fname,
                            fname, lnum, msg))
        self.logfd.flush()

    def critical(self, msg):
        """Log a message at CRITICAL level."""

        self(msg, self.CRITICAL)

    def error(self, msg):
        """Log a message at ERROR level."""

        self(msg, self.ERROR)

    def warn(self, msg):
        """Log a message at WARN level."""

        self(msg, self.WARN)

    def info(self, msg):
        """Log a message at INFO level."""

        self(msg, self.INFO)

    def debug(self, msg):
        """Log a message at DEBUG level."""

        self(msg, self.DEBUG)

    def dump_hex(self, msg, data, level=None):
        """Dump a string as hex.

        msg    'heading' string
        data   string to dump (bytes)
        level  logging level
        """

        HEXLEN = 48
        CHARLEN = 16

        # get level to log at
        if level is None:
            level = self.level

        def hexdump_line(s, offset):
            """Generate one line of fdump output.

            s       'bytes' to convert (16 bytes or less)
            offset  offset from start of dump
            """

            hex = ''
            char = ''
            for c in s:
                # convert to integer, if character was str to begin with
                try:
                    ordc = ord(c)
                except TypeError:
                    ordc = c        # nope, was byte, already integer
                hex += '%02x ' % ordc
                if ord(' ') <= ordc <= ord('~'):
                    char += chr(ordc)
                else:
                    char += '.'
            hex = (hex + ' '*HEXLEN)[:HEXLEN]
            char = (char + '|' + ' '*CHARLEN)[:CHARLEN+1]
            return '%04X  %s |%s  %d' % (offset, hex, char, offset)

        offset = 0
        dump = []
        while True:
            data = data[offset:offset + 16]
            if len(data) == 0:
                break
            dump.append(hexdump_line(data, offset))
            offset += 16

        self('%s:\n%s' % (msg, '\n'.join(dump)))

    def __del__(self):
        """Close the logging."""

        self.logfd.close()
        self.logfd = None
