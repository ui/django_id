#!/bin/sh
# full and incremental backup script
# created 07 February 2000
# Based on a script by Daniel O'Callaghan <danny@freebsd.org>
# and modified by Gerhard Mourani <gmourani@videotron.ca>

#Change the 5 variables below to fit your computer/backup

COMPUTER="%(host)s"                           # name of thiscomputer
DIRECTORIES="/srv/backup/data"                     	# directoris to backup
BACKUPDIR=/srv/backup/periodic                     	# where to store the backups
TIMEDIR=/srv/backup-scripts          # where to store timeoffullbackup
TAR=/bin/tar                            	# name and locaction of tar


