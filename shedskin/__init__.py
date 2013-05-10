'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2011 Mark Dufour; License GNU GPL version 3 (See LICENSE)

'''
import sys
import getopt
import os.path
import traceback
import time
import struct

import infer
import cpp
import annotate
import shared
import config


def usage():
    print """Usage: shedskin [OPTION]... FILE

 -a --ann               Output annotated source code (.ss.py)
 -b --nobounds          Disable bounds checking
 -e --extmod            Generate extension module
 -f --flags             Provide alternate Makefile flags
 -g --nogcwarns         Disable runtime GC warnings
 -l --long              Use long long ("64-bit") integers
 -m --makefile          Specify alternate Makefile name
 -n --silent            Silent mode, only show warnings
 -o --noassert          Disable assert statements
 -r --random            Use fast random number generator (rand())
 -s --strhash           Use fast string hashing algorithm (murmur)
 -w --nowrap            Disable wrap-around checking
 -x --traceback         Print traceback for uncaught exceptions
 -L --lib               Add a library directory
"""
# -p --pypy              Make extension module PyPy-compatible
# -v --msvc              Output MSVC-style Makefile
    sys.exit(1)


def start():
    config.setgx(config.newgx())

    # --- command-line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'vbchef:wad:m:rolspxngL:', ['help', 'extmod', 'nobounds', 'nowrap', 'flags=', 'debug=', 'makefile=', 'random', 'noassert', 'long', 'msvc', 'ann', 'strhash', 'pypy', 'traceback', 'silent', 'nogcwarns', 'lib'])
    except getopt.GetoptError:
        usage()

    for o, a in opts:
        if o in ['-h', '--help']:
            usage()
        if o in ['-b', '--nobounds']:
            config.getgx().bounds_checking = False
        if o in ['-e', '--extmod']:
            config.getgx().extension_module = True
        if o in ['-a', '--ann']:
            config.getgx().annotation = True
        if o in ['-d', '--debug']:
            config.getgx().debug_level = int(a)
        if o in ['-l', '--long']:
            config.getgx().longlong = True
        if o in ['-g', '--nogcwarns']:
            config.getgx().gcwarns = False
        if o in ['-w', '--nowrap']:
            config.getgx().wrap_around_check = False
        if o in ['-r', '--random']:
            config.getgx().fast_random = True
        if o in ['-o', '--noassert']:
            config.getgx().assertions = False
        if o in ['-p', '--pypy']:
            config.getgx().pypy = True
        if o in ['-m', '--makefile']:
            config.getgx().makefile_name = a
        if o in ['-n', '--silent']:
            config.getgx().silent = True
        if o in ['-s', '--strhash']:
            config.getgx().fast_hash = True
        if o in ['-v', '--msvc']:
            config.getgx().msvc = True
        if o in ['-x', '--traceback']:
            config.getgx().backtrace = True
        if o in ['-L', '--lib']:
            config.getgx().libdirs = [a] + config.getgx().libdirs
        if o in ['-f', '--flags']:
            if not os.path.isfile(a):
                print "*ERROR* no such file: '%s'" % a
                sys.exit(1)
            config.getgx().flags = a

    if not config.getgx().silent:
        print '*** SHED SKIN Python-to-C++ Compiler 0.9.3 ***'
        print 'Copyright 2005-2011 Mark Dufour; License GNU GPL version 3 (See LICENSE)'
        print

    # --- some checks
    major, minor = sys.version_info[:2]
    if (major, minor) not in [(2, 4), (2, 5), (2, 6), (2, 7)]:
        print '*ERROR* Shed Skin is not compatible with this version of Python'
        sys.exit(1)
    if sys.platform == 'win32' and os.path.isdir('c:/mingw'):
        print '*ERROR* please rename or remove c:/mingw, as it conflicts with Shed Skin'
        sys.exit()
    if sys.platform == 'win32' and struct.calcsize('P') == 8 and config.getgx().extension_module:
        print '*WARNING* 64-bit python may not come with necessary file to build extension module'

    # --- argument
    if len(args) != 1:
        usage()
    name = args[0]
    if not name.endswith('.py'):
        name += '.py'
    if not os.path.isfile(name):
        print "*ERROR* no such file: '%s'" % name
        sys.exit(1)
    main_module_name = os.path.splitext(name)[0]

    # --- analyze & annotate
    t0 = time.time()
    infer.analyze(main_module_name)
    annotate.annotate()
    cpp.generate_code()
    shared.print_errors()
    if not config.getgx().silent:
        print '[elapsed time: %.2f seconds]' % (time.time() - t0)


def main():
    sys.setrecursionlimit(100000)
    try:
        start()
    except KeyboardInterrupt, e:
        if config.getgx().debug_level > 0:
            print traceback.format_exc(e)
        sys.exit(1)

if __name__ == '__main__':
    main()
