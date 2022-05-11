#!/usr/bin/env python
# coding=utf-8
'''
Author: penfree
Date: 2022-01-22 01:12:32

'''
from sys import stdout
from tempfile import NamedTemporaryFile
from argparse import ArgumentParser
import logging
logging.basicConfig(level=logging.INFO)

def getArgs():
    parser = ArgumentParser()
    parser.add_argument('-f', '--script', dest='script_file')
    parser.add_argument('-m', '--module', dest='module')
    parser.add_argument('--port', dest='port', default='8503')
    return parser.parse_args()

def main():
    args = getArgs()
    template = f'''
from webargparse.homepage import Homepage
Homepage.run()
'''
    f = NamedTemporaryFile(mode='w', delete=False, suffix='.py')
    f.write(template)
    f.flush()
    f.close()
    logging.info('entrypoint generated at %s', f.name)
    import subprocess, os, pathlib, sys
    my_env = os.environ.copy()
    if args.script_file:
        my_env['WEB_ARGPARSE_MODULE_NAME'] = pathlib.Path(args.script_file).stem
        my_env['PYTHONPATH'] = my_env['PYTHONPATH'] + ':' + pathlib.Path(args.script_file).parent.as_posix()
    elif args.module:
        my_env['WEB_ARGPARSE_MODULE_NAME'] = args.module
    ret = subprocess.run('streamlit run  %s  --browser.gatherUsageStats=false --server.port %s --server.headless true' % (f.name, args.port), env=my_env, shell=True, stderr=subprocess.STDOUT, check=True)
    print(ret)

if __name__ == '__main__':
    main()
