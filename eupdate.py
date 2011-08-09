#!/usr/bin/env python

#
# This is a simple script for Gentoo portage, layman and eix updating.
#
# Homepage: https://github.com/p0deje/eupdate
#

from __future__ import print_function
import portage
import sys
from subprocess import Popen, PIPE
from os import getuid

vartree = portage.db[portage.root]['vartree']
log_file = '/var/log/eupdate.log'

# Binaries
emerge_bin = '/usr/bin/emerge'
layman_bin = '/usr/bin/layman'
eix_update_bin = '/usr/bin/eix-update'
eix_diff_bin = '/usr/bin/eix-diff'
notify_bin = '/usr/bin/notify-send'

def main():
    # Print help
    if len(sys.argv) == 1 or 'h' in sys.argv[1]:
        _print_help()
    # Check permissions
    if not _is_root():
        raise RuntimeError, 'Not enough permissions! Make sure you run it as root.'
    # Open log file
    log = open(log_file, 'a')
    # Update portage
    print('Updating portage. Please, wait...')
    emerge = Popen([emerge_bin] + ['--sync'], stdout=PIPE)
    while emerge.stdout.readline():
        log.write(emerge.stdout.readline())
    # Update layman
    if _is_layman_installed():
        print('Updating layman. Please, wait...')
        layman = Popen([layman_bin] + ['-S'], stdout=PIPE)
        while layman.stdout.readline():
            log.write(layman.stdout.readline())
    # Update eix
    if _is_eix_installed():
        print('Updating eix. Please, wait...')
        eix = Popen([eix_update_bin], stdout=PIPE)
        while eix.stdout.readline():
            log.write(eix.stdout.readline())
        # Print eix-diff if necessary
        if len(sys.argv) > 1 and 'd' in sys.argv[1]:
            Popen([eix_diff_bin] + ['/var/cache/eix.previous'] + ['/var/cache/eix']).wait()
    # Send notification
    if len(sys.argv) > 1 and 'n' in sys.argv[1]:
        header = 'Update is complete'
        msg = 'Synchronization of layman, portage and eix is complete. You are now free to emerge -auvDN world.'
        Popen([notify_bin] + [header] + [msg])

def _print_help():
    print("""eupdate - Dirty little script for portage, layman and eix update.
https://github.com/p0deje/eupdate

Usage:
    ./eupdate.py [-dn]

Options:
    (d)iff      - run eix-diff to show difference after update
    (n)otify    - show notification (via notify-send) when everything is done
    (h)elp      - show this help""")
    sys.exit(0)

def _is_layman_installed():
    return bool(vartree.dep_bestmatch('app-portage/layman'))

def _is_eix_installed():
    return bool(vartree.dep_bestmatch('app-portage/eix'))

def _is_root():
    return getuid() == 0

if __name__ == '__main__':
    main()
