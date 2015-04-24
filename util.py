#!/usr/bin/env python3  
#coding: utf-8 


import os
import platform
import subprocess
import sys
import time
import re

ON_LINUX = (platform.system() == 'Linux')
conf = {
    'max_domains': 10,
    'max_ext_length': 10,
    'style': 'gitstats.css',
    'max_authors': 20,
    'authors_top': 5,
    'commit_begin': '',
    'commit_end': 'HEAD',
    'linear_linestats': 1,
    'project_name': '',
    'processes': 8,
    'start_date': ''
}
class Util():

    @staticmethod
    def getpipeoutput(cmds, quiet = False):
        global exectime_external
        start = time.time()
        if not quiet and ON_LINUX and os.isatty(1):
            print ('~~~~~~~~ ' + ' | '.join(cmds),)
            sys.stdout.flush()
        p = subprocess.Popen(cmds[0], stdout = subprocess.PIPE, shell = True)
        processes=[p]
        for x in cmds[1:]:
            p = subprocess.Popen(x, stdin = p.stdout, stdout = subprocess.PIPE, shell = True)
            processes.append(p)
        output = p.communicate()[0]
        for p in processes:
            p.wait()
        end = time.time()
        if not quiet:
            if ON_LINUX and os.isatty(1):
                #print ("\r",)
                print("")
            #print ('[%.5f] >> %s' % (end - start, ' | '.join(cmds)))
        #exectime_external += (end - start)
 
        return output.rstrip('\n')

    @staticmethod
    def getlogrange(defaultrange = 'HEAD', end_only = True):
        commit_range = Util.getcommitrange(defaultrange, end_only)
        if len(conf['start_date']) > 0:
            return '--since=%s %s' % (conf['start_date'], commit_range)
        return commit_range
   
    @staticmethod
    def getcommitrange(defaultrange = 'HEAD', end_only = False):
        if len(conf['commit_end']) > 0:
            if end_only or len(conf['commit_begin']) == 0:
                return conf['commit_end']
            return '%s..%s' % (conf['commit_begin'], conf['commit_end'])
        return defaultrange

    @staticmethod
    def getstatsummarycounts(line):
        numbers = re.findall('\d+', line)
        if   len(numbers) == 1:
            # neither insertions nor deletions: may probably only happen for "0 files changed"
            numbers.append(0);
            numbers.append(0);
        elif len(numbers) == 2 and line.find('(+)') != -1:
            numbers.append(0);    # only insertions were printed on line
        elif len(numbers) == 2 and line.find('(-)') != -1:
            numbers.insert(1, 0); # only deletions were printed on line
        return numbers